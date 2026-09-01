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


# Feature order is a contract: the exported JS takes a plain array, so this
# list must stay in lockstep with `ml_features` in src/scenes/Level.ts.
#
# 'avgTimeBetweenJumps' is deliberately NOT a feature. It is derived from
# (jumpStartTime - landTime) in Level.applyJump(), which also counts time the
# scene spent paused — a pause of 22s was observed inflating it from 1083ms to
# 22992ms. Since sessions where the player paused were mostly abandoned, the
# model learned "player paused" as a proxy for "player will quit" and pinned
# the prediction low for the rest of the run, ignoring level progress.
# The column is still collected and stored; it is just not trained on.
FEATURES = [
    'jumpSuccessRate', 'jumpsFailed', 'totalFalls', 'maxFallDistance',
    'distancePerJump', 'totalJumpsAttempted',
    'velocity_magnitude', 'pos_x', 'pos_y'
]
TARGET = 'Will_Finish'


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
