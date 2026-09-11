"""
models.py
shared feature set and model definitions, used by training and evaluation alike.
"""

import xgboost as xgb
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier


# feature order is a contract: the exported js takes a plain array, so this
# list must match `ml_features` in src/scenes/Level.ts.
#
# avgTimeBetweenJumps is deliberately not a feature: it included time the
# scene spent paused, and the model learned 'player paused' as a proxy for
# 'player will quit' (section 5.4). the column is still stored, not trained on.
FEATURES = [
    'jumpSuccessRate', 'jumpsFailed', 'totalFalls', 'maxFallDistance',
    'distancePerJump', 'totalJumpsAttempted',
    'velocity_magnitude', 'pos_x', 'pos_y'
]
TARGET = 'Will_Finish'


def make_logistic_regression():
    """baseline: linear model, expects standardised features."""
    return LogisticRegression(max_iter=1000, random_state=42)


def make_decision_tree():
    """baseline: single shallow tree on raw features."""
    return DecisionTreeClassifier(max_depth=4, random_state=42)


def make_xgboost():
    """main model. kept shallow so the exported js stays small."""
    return xgb.XGBClassifier(
        n_estimators=30,
        max_depth=3,
        learning_rate=0.1,
        random_state=42,
        base_score=0.5  # set explicitly for m2cgen compatibility
    )
