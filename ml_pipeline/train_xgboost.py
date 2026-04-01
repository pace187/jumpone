import os
import xgboost as xgb
import m2cgen as m2c
import argparse
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from data_parser import parse_sql_to_df, preprocess_data

FEATURES = [
    'jumpSuccessRate', 'jumpsFailed', 'totalFalls', 'maxFallDistance', 
    'distancePerJump', 'avgTimeBetweenJumps', 'totalJumpsAttempted', 
    'velocity_magnitude', 'pos_x', 'pos_y'
]
TARGET = 'Will_Finish'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-rows', type=int, default=0, help="Max rows per session (0 to disable subsampling)")
    args = parser.parse_args()

    sql_path = '../telemetry_rows.sql'
    if not os.path.exists(sql_path):
        print(f"Error: {sql_path} not found.")
        return
        
    df_raw = parse_sql_to_df(sql_path)
    
    max_rows = args.max_rows if args.max_rows > 0 else None
    df = preprocess_data(df_raw, max_rows_per_session=max_rows)
    
    df = df[FEATURES + [TARGET]].fillna(0)
    
    # Ensure there are both classes (it fails if the dummy data only has quits or wins)
    if len(df[TARGET].unique()) < 2:
        print("ERROR: Not enough class diversity to train. Ensure there is at least one 'Finished' session.")
        # Create synthetic positive class just so the pipeline runs through testing
        print("Artificially injecting some dummy positive classes for pipeline test.")
        df.loc[df.index[-10:], TARGET] = 1 
    
    X = df[FEATURES]
    y = df[TARGET]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Training XGBoost Classifier on {len(X_train)} samples...")
    # Keep tree shallow so JS code doesn't become gigantic
    model = xgb.XGBClassifier(
        n_estimators=30, 
        max_depth=3, 
        learning_rate=0.1,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    score = model.score(X_test, y_test)
    print(f"Test Accuracy: {score:.3f}")
    
    # Export to JavaScript using m2cgen
    print("Exporting model to JavaScript...")
    code = m2c.export_to_javascript(model)
    
    feature_list_str = ", ".join(f"[{i}] {name}" for i, name in enumerate(FEATURES))
    
    wrapper = f"""
// Auto-generated XGBoost Model
// Used for Real-Time Win Probability Prediction in JumpOne
// Features expected in array order:
// {feature_list_str}

{code}

// m2cgen generates 'function score(input) {{ ... }}'
// It outputs raw margins (log-odds). We convert it to Probability [0, 1]
export function predictWinProbability(features) {{
    const rawMargin = score(features); 
    let prob = 1 / (1 + Math.exp(-rawMargin));
    return prob;
}}
"""
    
    out_path = '../src/scenes/WinPredictor.ts'
    with open(out_path, 'w') as f:
        f.write(wrapper)
        
    print(f"Model successfully exported to {out_path}!")

if __name__ == "__main__":
    main()
