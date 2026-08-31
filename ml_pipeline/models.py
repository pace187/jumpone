"""
models.py
Shared model definitions for the JumpOne ML pipeline.

train_xgboost.py (export) and visualize_results.py (figures) must use identical
hyperparameters, otherwise the plots describe a different model than the one
shipped in the game. Defining them once here keeps both in sync.
"""

import xgboost as xgb
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier


def make_logistic_regression():
    """Baseline: linear model, expects standardised features."""
    return LogisticRegression(max_iter=1000, random_state=42)


def make_decision_tree():
    """Baseline: single shallow tree, trained on raw features."""
    return DecisionTreeClassifier(max_depth=4, random_state=42)


def make_xgboost():
    """Main model. Kept shallow so the exported JS doesn't become gigantic."""
    return xgb.XGBClassifier(
        n_estimators=30,
        max_depth=3,
        learning_rate=0.1,
        random_state=42,
        base_score=0.5  # explizit setzen für m2cgen-Kompatibilität
    )
