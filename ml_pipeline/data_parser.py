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

def parse_sql_to_df(filepath):
    print(f"Reading {filepath}...")
    with open(filepath, 'r') as f:
        content = f.read()

    m = re.search(r'\(\s*\d+\s*,', content)
    if m is None:
        raise ValueError("Konnte keinen Datenbeginn in der SQL-Datei finden.")

    data_str = content[m.start():].strip()

    # Abschließendes Semikolon entfernen
    if data_str.endswith(';'):
        data_str = data_str[:-1].rstrip()

    # Tupel-Trennzeichen normalisieren → Zeilenumbrüche
    data_str = re.sub(r'\)\s*,\s*\n?\s*\(', '\n', data_str)

    # Umschließende Klammern jeder Zeile entfernen
    lines = []
    for line in data_str.splitlines():
        line = line.strip()
        if line.startswith('('):
            line = line[1:]
        if line.endswith(')'):
            line = line[:-1]
        if line:
            lines.append(line)

    # SQL-Anführungszeichen entfernen ('Idle' -> Idle)
    clean = "\n".join(lines).replace("'", "")

    print(f"Parsing CSV data... ({len(lines)} Zeilen)")
    df = pd.read_csv(io.StringIO(clean), names=COLUMNS, header=None)
    df['state'] = df['state'].astype(str).str.strip()
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
    
    # 1 if ANY row in the session is 'Finished', 0 otherwise (represents a Quit or Ragequit)
    session_outcomes = df.groupby('session_id')['state'].apply(lambda x: 1 if (x == 'Finished').any() else 0)
    df['Will_Finish'] = df['session_id'].map(session_outcomes)
    
    # Drop rows that are actual outcome states (we don't train on them, we train on intermediate gameplay)
    df = df[~df['state'].isin(['Finished', 'Quit'])]
    
    # --- Subsampling for Bias Prevention ---
    if max_rows_per_session is not None:
        print(f"Subsampling: Limiting to a maximum of {max_rows_per_session} random rows per session to prevent bias...")
        df = df.groupby('session_id', group_keys=False).apply(
            lambda x: x.sample(n=min(len(x), max_rows_per_session), random_state=42)
        )
        # Restore original chronological sorting by numeric index
        df = df.sort_index()

    return df

def aggregate_per_session(df):
    """One row per session: cumulative cols from last row, snapshot cols averaged."""
    df_sorted = df.sort_values(['session_id', 'timestamp'])
    last_rows = df_sorted.groupby('session_id')[CUMULATIVE_FEATURES + ['Will_Finish']].last()
    mean_rows = df_sorted.groupby('session_id')[SNAPSHOT_FEATURES].mean()
    return last_rows.join(mean_rows)
