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

# Alle Skripte lesen denselben Export. Hier steht der Standardpfad einmal;
# jedes Skript nimmt ihn per --sql entgegen, damit man mehrere Exporte
# nebeneinander auswerten kann, ohne Dateien umzubenennen.
DEFAULT_SQL = "../telemetry_rows.sql"


def add_sql_argument(parser, default=DEFAULT_SQL):
    """Haengt den einheitlichen --sql-Schalter an einen ArgumentParser."""
    parser.add_argument(
        "--sql", default=default, metavar="PFAD",
        help=f"Pfad zum SQL-Export (Standard: {default})",
    )
    return parser

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
    # Spaltennamen erst nach dem Einlesen zuweisen: Exporte von vor der
    # Einfuehrung von player_id haben eine Spalte weniger. Beide muessen lesbar
    # bleiben, sonst sind die Altdaten mit der neuen Pipeline nicht mehr nutzbar.
    df = pd.read_csv(io.StringIO(clean), header=None)
    if df.shape[1] == len(COLUMNS):
        df.columns = COLUMNS
        df['player_id'] = pd.NA          # Altdaten: Person unbekannt
    elif df.shape[1] == len(COLUMNS) + 1:
        df.columns = COLUMNS + ['player_id']
    else:
        raise ValueError(
            f"Unerwartete Spaltenzahl im Export: {df.shape[1]}, "
            f"erwartet {len(COLUMNS)} oder {len(COLUMNS)+1}. "
            f"Wurde das Tabellenschema geaendert? Dann COLUMNS anpassen."
        )
    # Werte hinter ", " tragen ein fuehrendes Leerzeichen. Ohne Strip vergleichen
    # sich session_ids aus zwei Exporten nicht zuverlaessig.
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
    
    # 1 if ANY row in the session is 'Finished', 0 otherwise (represents a Quit or Ragequit)
    session_outcomes = df.groupby('session_id')['state'].apply(lambda x: 1 if (x == 'Finished').any() else 0)
    df['Will_Finish'] = df['session_id'].map(session_outcomes)
    
    # Drop rows that are actual outcome states (we don't train on them, we train on intermediate gameplay)
    df = df[~df['state'].isin(['Finished', 'Quit'])]
    
    # --- Subsampling for Bias Prevention ---
    if max_rows_per_session is not None:
        print(f"Subsampling: Limiting to a maximum of {max_rows_per_session} random rows per session to prevent bias...")
        # Bewusst kein groupby(...).apply(): neuere pandas-Versionen entfernen dabei
        # die Gruppenspalte aus dem Ergebnis, wodurch 'session_id' still verschwindet.
        parts = [
            g.sample(n=min(len(g), max_rows_per_session), random_state=42)
            for _, g in df.groupby('session_id', sort=False)
        ]
        # Restore original chronological sorting by numeric index
        df = pd.concat(parts).sort_index()

    return df

def aggregate_per_session(df):
    """One row per session: cumulative cols from last row, snapshot cols averaged."""
    df_sorted = df.sort_values(['session_id', 'timestamp'])
    last_rows = df_sorted.groupby('session_id')[CUMULATIVE_FEATURES + ['Will_Finish']].last()
    mean_rows = df_sorted.groupby('session_id')[SNAPSHOT_FEATURES].mean()
    return last_rows.join(mean_rows)
