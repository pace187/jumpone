import os
import pandas as pd
import io
import re

COLUMNS = [
    "id", "created_at", "session_id", "pos_x", "pos_y", "vel_x", "vel_y",
    "velocity_magnitude", "input_left", "input_right", "input_jump", "state",
    "timestamp", "jumpSuccessRate", "jumpsFailed", "avgFallDistance",
    "maxFallDistance", "distancePerJump", "avgTimeBetweenJumps",
    "totalJumpsAttempted", "sessionDuration_sec", "totalFalls"
]

# default export path; every script takes --sql so several exports can be
# evaluated side by side without renaming files.
DEFAULT_SQL = "../telemetry_rows.sql"


def add_sql_argument(parser, default=DEFAULT_SQL):
    """adds the shared --sql option to an ArgumentParser."""
    parser.add_argument(
        "--sql", default=default, metavar="PFAD",
        help=f"path to the sql export (default: {default})",
    )
    return parser

def parse_sql_to_df(filepath):
    print(f"Reading {filepath}...")
    with open(filepath, 'r') as f:
        content = f.read()

    m = re.search(r'\(\s*\d+\s*,', content)
    if m is None:
        raise ValueError("no data start found in the sql file.")

    data_str = content[m.start():].strip()

    # drop the trailing semicolon
    if data_str.endswith(';'):
        data_str = data_str[:-1].rstrip()

    # one tuple per line
    data_str = re.sub(r'\)\s*,\s*\n?\s*\(', '\n', data_str)

    # strip the parentheses around each row
    lines = []
    for line in data_str.splitlines():
        line = line.strip()
        if line.startswith('('):
            line = line[1:]
        if line.endswith(')'):
            line = line[:-1]
        if line:
            lines.append(line)

    # strip sql quotes ('Idle' -> Idle)
    clean = "\n".join(lines).replace("'", "")

    print(f"parsing csv data... ({len(lines)} rows)")
    # assign column names after reading: exports from before player_id have
    # one column less, and both must stay readable.
    df = pd.read_csv(io.StringIO(clean), header=None)
    if df.shape[1] == len(COLUMNS):
        df.columns = COLUMNS
        df['player_id'] = pd.NA          # legacy rows: player unknown
    elif df.shape[1] == len(COLUMNS) + 1:
        df.columns = COLUMNS + ['player_id']
    else:
        raise ValueError(
            f"unexpected column count in export: {df.shape[1]}, "
            f"expected {len(COLUMNS)} or {len(COLUMNS)+1}. "
            f"has the table schema changed? then adjust COLUMNS."
        )
    # values after ', ' carry a leading space; without strip, session_ids from
    # two exports do not compare reliably.
    df['state'] = df['state'].astype(str).str.strip()
    df['session_id'] = df['session_id'].astype(str).str.strip()
    if 'player_id' in df.columns:
        df['player_id'] = df['player_id'].astype(str).str.strip().replace({'': pd.NA, '<NA>': pd.NA})
    return df


CUMULATIVE_FEATURES = [
    'jumpSuccessRate', 'jumpsFailed', 'totalFalls', 'avgFallDistance',
    'maxFallDistance', 'distancePerJump', 'avgTimeBetweenJumps', 'totalJumpsAttempted',
]
SNAPSHOT_FEATURES = [
    'velocity_magnitude', 'pos_x', 'pos_y'
]

def preprocess_data(df, max_rows_per_session=None):
    print("Sorting and propagating labels...")
    df = df.sort_values(by=['session_id', 'timestamp'])
    
    # ml_pipeline/data_parser.py, preprocess_data()

    # 1 if any row in the session is 'Finished', 0 otherwise
    session_outcomes = df.groupby('session_id')['state'].apply(lambda x: 1 if (x == 'Finished').any() else 0)
    df['Will_Finish'] = df['session_id'].map(session_outcomes)
    
    # drop the terminal rows; training uses intermediate gameplay only
    df = df[~df['state'].isin(['Finished', 'Quit'])]
    
    # --- subsampling ---
    if max_rows_per_session is not None:
        print(f"Subsampling: Limiting to a maximum of {max_rows_per_session} random rows per session to prevent bias...")
        # no groupby(...).apply(): newer pandas drops the group column from the
        # result and 'session_id' silently disappears.
        parts = [
            g.sample(n=min(len(g), max_rows_per_session), random_state=42)
            for _, g in df.groupby('session_id', sort=False)
        ]
        # restore chronological order via the numeric index
        df = pd.concat(parts).sort_index()

    return df

def aggregate_per_session(df):
    """one row per session: cumulative columns from the last row, snapshot columns averaged."""
    df_sorted = df.sort_values(['session_id', 'timestamp'])
    last_rows = df_sorted.groupby('session_id')[CUMULATIVE_FEATURES + ['Will_Finish']].last()
    mean_rows = df_sorted.groupby('session_id')[SNAPSHOT_FEATURES].mean()
    return last_rows.join(mean_rows)
