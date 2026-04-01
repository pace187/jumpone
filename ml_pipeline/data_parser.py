import os
import pandas as pd
import io

def parse_sql_to_df(filepath):
    print(f"Reading {filepath}...")
    with open(filepath, 'r') as f:
        content = f.read()

    start_idx = content.find('VALUES (')
    if start_idx == -1:
        raise ValueError("Could not find 'VALUES (' in the SQL file")
    
    data_str = content[start_idx + 8 :].strip()
    if data_str.endswith(');'):
        data_str = data_str[:-2]
    elif data_str.endswith(')'):
        data_str = data_str[:-1]
    
    data_str = data_str.replace("), (", "\n")
    data_str = data_str.replace("'", "")
    
    columns = [
        "id", "created_at", "session_id", "pos_x", "pos_y", "vel_x", "vel_y", 
        "velocity_magnitude", "input_left", "input_right", "input_jump", "state", 
        "timestamp", "jumpSuccessRate", "jumpsFailed", "avgFallDistance", 
        "maxFallDistance", "distancePerJump", "avgTimeBetweenJumps", 
        "totalJumpsAttempted", "sessionDuration_sec", "totalFalls"
    ]
    
    print("Parsing CSV data...")
    df = pd.read_csv(io.StringIO(data_str), names=columns, header=None)
    df['state'] = df['state'].str.strip()
    return df

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
