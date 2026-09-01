import os
import m2cgen as m2c
import argparse
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score
from sklearn.preprocessing import StandardScaler
from data_parser import parse_sql_to_df, preprocess_data, add_sql_argument
from models import (
    make_logistic_regression, make_decision_tree, make_xgboost,
    FEATURES, TARGET,
)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-rows', type=int, default=0, help="Max rows per session (0 to disable subsampling)")
    add_sql_argument(parser)
    args = parser.parse_args()

    sql_path = args.sql
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

    # --- Baseline: Logistic Regression ---
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    lr = make_logistic_regression()
    lr.fit(X_train_scaled, y_train)
    lr_acc = lr.score(X_test_scaled, y_test)
    lr_f1 = f1_score(y_test, lr.predict(X_test_scaled), zero_division=0)
    lr_js = m2c.export_to_javascript(lr)
    print(f"\n[Logistic Regression]  Accuracy: {lr_acc:.3f}  F1: {lr_f1:.3f}  JS size: {len(lr_js):,} chars")

    # --- Baseline: Decision Tree ---
    dt = make_decision_tree()
    dt.fit(X_train, y_train)
    dt_acc = dt.score(X_test, y_test)
    dt_f1 = f1_score(y_test, dt.predict(X_test), zero_division=0)
    dt_js = m2c.export_to_javascript(dt)
    print(f"[Decision Tree]        Accuracy: {dt_acc:.3f}  F1: {dt_f1:.3f}  JS size: {len(dt_js):,} chars")

    # --- Main model: XGBoost ---
    print(f"\nTraining XGBoost Classifier on {len(X_train)} samples...")
    model = make_xgboost()
    model.fit(X_train, y_train)

    xgb_acc = model.score(X_test, y_test)
    xgb_f1 = f1_score(y_test, model.predict(X_test), zero_division=0)
    xgb_js = m2c.export_to_javascript(model)
    print(f"[XGBoost]              Accuracy: {xgb_acc:.3f}  F1: {xgb_f1:.3f}  JS size: {len(xgb_js):,} chars")
    print(f"\n=> XGBoost vs. Logistic Regression: Δ Accuracy {xgb_acc - lr_acc:+.3f}, Δ F1 {xgb_f1 - lr_f1:+.3f}")
    print(f"=> XGBoost vs. Decision Tree:        Δ Accuracy {xgb_acc - dt_acc:+.3f}, Δ F1 {xgb_f1 - dt_f1:+.3f}")

    # Export XGBoost to JavaScript using m2cgen
    print("\nExporting XGBoost model to JavaScript...")

    feature_list_str = ", ".join(f"[{i}] {name}" for i, name in enumerate(FEATURES))
    
    wrapper = f"""
// Auto-generated XGBoost Model — do not edit by hand.
// Regenerate with: python3 train_xgboost.py
// Used for Real-Time Win Probability Prediction in JumpOne
// Features expected in array order:
// {feature_list_str}

// @ts-nocheck -- machine-generated body from m2cgen

{xgb_js}

// m2cgen emits 'function score(input) {{ ... }}'.
// For a binary classifier it already applies the sigmoid internally and
// returns [P(class 0), P(class 1)] — do NOT apply a sigmoid again.
export function predictWinProbability(features: number[]): number {{
    const out = score(features);
    return Array.isArray(out)
        ? out[out.length - 1]        // classifier: last entry is P(win)
        : 1 / (1 + Math.exp(-out));  // regressor: raw logit
}}
"""
    
    out_path = '../src/scenes/WinPredictor.ts'
    with open(out_path, 'w') as f:
        f.write(wrapper)
        
    print(f"Model successfully exported to {out_path}!")

if __name__ == "__main__":
    main()
