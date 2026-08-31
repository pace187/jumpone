"""
visualize_results.py
Generates publication-quality figures for the bachelor thesis.

Output: ml_pipeline/plots/
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats as sp_stats
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    confusion_matrix, roc_curve, auc,
    f1_score, ConfusionMatrixDisplay
)
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from data_parser import parse_sql_to_df, preprocess_data, aggregate_per_session
from models import make_logistic_regression, make_decision_tree, make_xgboost

# ── Stil ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":      "DejaVu Sans",
    "font.size":        12,
    "axes.titlesize":   14,
    "axes.titleweight": "bold",
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "figure.dpi":       150,
    "savefig.dpi":      300,
    "savefig.bbox":     "tight",
})
PALETTE   = ["#4C72B0", "#DD8452", "#55A868"]   # LR / DT / XGB
OUT_DIR   = "plots"
SQL_PATH  = "../telemetry_rows.sql"
FEATURES  = [
    'jumpSuccessRate', 'jumpsFailed', 'totalFalls', 'maxFallDistance',
    'distancePerJump', 'avgTimeBetweenJumps', 'totalJumpsAttempted',
    'velocity_magnitude', 'pos_x', 'pos_y'
]
TARGET = 'Will_Finish'

FEATURE_LABELS = {
    'jumpSuccessRate':     'Jump Success Rate',
    'jumpsFailed':         'Jumps Failed',
    'totalFalls':          'Total Falls',
    'maxFallDistance':     'Max Fall Distance',
    'distancePerJump':     'Distance per Jump',
    'avgTimeBetweenJumps': 'Avg. Time Between Jumps',
    'totalJumpsAttempted': 'Total Jumps Attempted',
    'velocity_magnitude':  'Velocity Magnitude',
    'pos_x':               'Position X',
    'pos_y':               'Position Y',
}

os.makedirs(OUT_DIR, exist_ok=True)


# ── Train models ────────────────────────────────────────────────────────────
def train_models(df):
    print("Training models...")
    df = df[FEATURES + [TARGET]].fillna(0)

    X = df[FEATURES]
    y = df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler        = StandardScaler()
    X_train_sc    = scaler.fit_transform(X_train)
    X_test_sc     = scaler.transform(X_test)

    lr = make_logistic_regression()
    lr.fit(X_train_sc, y_train)

    dt = make_decision_tree()
    dt.fit(X_train, y_train)

    model = make_xgboost()
    model.fit(X_train, y_train)

    return (lr, dt, model), (X_train, X_test, X_train_sc, X_test_sc, y_train, y_test)


# ── Plot 1: Model Comparison (Accuracy + F1) ───────────────────────────────
def plot_model_comparison(models, data):
    lr, dt, xgb_m = models
    X_train, X_test, X_train_sc, X_test_sc, y_train, y_test = data

    names  = ["Logistic\nRegression", "Decision\nTree", "XGBoost"]
    accs   = [
        lr.score(X_test_sc, y_test),
        dt.score(X_test, y_test),
        xgb_m.score(X_test, y_test),
    ]
    f1s = [
        f1_score(y_test, lr.predict(X_test_sc),  zero_division=0),
        f1_score(y_test, dt.predict(X_test),      zero_division=0),
        f1_score(y_test, xgb_m.predict(X_test),   zero_division=0),
    ]

    x     = np.arange(len(names))
    width = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))

    bars1 = ax.bar(x - width/2, accs, width, label="Accuracy", color=PALETTE, alpha=0.9)
    bars2 = ax.bar(x + width/2, f1s,  width, label="F1-Score",  color=PALETTE, alpha=0.5,
                   hatch="//", edgecolor="white")

    for bar in list(bars1) + list(bars2):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                f"{bar.get_height():.3f}", ha="center", va="bottom", fontsize=10)

    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Score")
    ax.set_title("Model Comparison: Accuracy & F1-Score")
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.legend()
    ax.yaxis.grid(True, alpha=0.3)
    ax.set_axisbelow(True)

    path = f"{OUT_DIR}/model_comparison.png"
    plt.savefig(path)
    plt.close()
    print(f"  ✓ {path}")


# ── Plot 2: ROC Curves ──────────────────────────────────────────────────────
def plot_roc_curves(models, data):
    lr, dt, xgb_m = models
    _, X_test, _, X_test_sc, _, y_test = data

    fig, ax = plt.subplots(figsize=(7, 6))

    configs = [
        ("Logistic Regression", lr,    X_test_sc, PALETTE[0]),
        ("Decision Tree",       dt,    X_test,    PALETTE[1]),
        ("XGBoost",             xgb_m, X_test,    PALETTE[2]),
    ]
    for name, clf, X, color in configs:
        proba = clf.predict_proba(X)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, proba)
        roc_auc = auc(fpr, tpr)
        ax.plot(fpr, tpr, color=color, lw=2,
                label=f"{name}  (AUC = {roc_auc:.3f})")

    ax.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5, label="Random Classifier")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curves – Model Comparison")
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)

    path = f"{OUT_DIR}/roc_curves.png"
    plt.savefig(path)
    plt.close()
    print(f"  ✓ {path}")


# ── Plot 3: Feature Importance (XGBoost) ────────────────────────────────────
def plot_feature_importance(models, data):
    _, _, xgb_m = models
    importances = xgb_m.feature_importances_
    labels      = [FEATURE_LABELS[f] for f in FEATURES]
    order       = np.argsort(importances)

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.barh(
        [labels[i] for i in order],
        importances[order],
        color="#4C72B0", alpha=0.85
    )
    for bar in bars:
        ax.text(bar.get_width() + 0.002, bar.get_y() + bar.get_height()/2,
                f"{bar.get_width():.3f}", va="center", fontsize=9)

    ax.set_xlabel("Feature Importance (Gain)")
    ax.set_title("XGBoost – Feature Importance")
    ax.xaxis.grid(True, alpha=0.3)
    ax.set_axisbelow(True)

    path = f"{OUT_DIR}/feature_importance.png"
    plt.savefig(path)
    plt.close()
    print(f"  ✓ {path}")


# ── Plot 4: Confusion Matrix (XGBoost) ─────────────────────────────────────
def plot_confusion_matrix(models, data):
    _, _, xgb_m = models
    _, X_test, _, _, _, y_test = data

    cm = confusion_matrix(y_test, xgb_m.predict(X_test))
    fig, ax = plt.subplots(figsize=(5, 4))
    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["Not Finished (0)", "Finished (1)"]
    )
    disp.plot(ax=ax, colorbar=False, cmap="Blues")
    ax.set_title("Confusion Matrix – XGBoost")
    ax.set_xlabel("Predicted Label")
    ax.set_ylabel("True Label")
    plt.tight_layout()

    path = f"{OUT_DIR}/confusion_matrix.png"
    plt.savefig(path)
    plt.close()
    print(f"  ✓ {path}")


# ── Plot 5: Win Probability Over Time (example sessions) ───────────────────
def plot_win_probability_over_time(models, df):
    """Shows how estimated win probability evolves throughout a session."""
    _, _, xgb_m = models
    df = df.fillna(0)

    # Pick one finished session and one quit session
    finished_sessions = df[df['Will_Finish'] == 1]['session_id'].unique()
    quit_sessions     = df[df['Will_Finish'] == 0]['session_id'].unique()

    if len(finished_sessions) == 0 or len(quit_sessions) == 0:
        print("  ⚠ Not enough sessions for win-probability plot.")
        return

    fig, ax = plt.subplots(figsize=(10, 5))

    for sid, label, color in [
        (finished_sessions[0], "Completed Session (Will_Finish=1)", "#55A868"),
        (quit_sessions[0],     "Abandoned Session (Will_Finish=0)", "#C44E52"),
    ]:
        session = df[df['session_id'] == sid][FEATURES].fillna(0)
        if len(session) < 10:
            continue
        probs = xgb_m.predict_proba(session)[:, 1]
        # Normalize time axis to [0, 100%]
        x = np.linspace(0, 100, len(probs))
        ax.plot(x, probs, label=label, color=color, lw=2, alpha=0.85)
        ax.fill_between(x, probs, alpha=0.1, color=color)

    ax.axhline(0.5, color="gray", lw=1, linestyle="--", alpha=0.6, label="50% Threshold")
    ax.set_xlabel("Game Progress (%)")
    ax.set_ylabel("Estimated Win Probability")
    ax.set_title("Win Probability Over Game Progress (XGBoost)")
    ax.set_ylim(0, 1)
    ax.legend()
    ax.grid(alpha=0.3)

    path = f"{OUT_DIR}/win_probability_over_time.png"
    plt.savefig(path)
    plt.close()
    print(f"  ✓ {path}")


# ── Plot 6: Class Distribution in Dataset ───────────────────────────────────
def plot_class_distribution(df):
    per_session = df.groupby('session_id')['Will_Finish'].first()
    counts = per_session.value_counts().sort_index()
    labels = ["Not Finished\n(Quit/Idle)", "Finished"]
    colors = ["#C44E52", "#55A868"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # Pie
    ax1.pie(counts, labels=labels, colors=colors, autopct="%1.0f%%",
            startangle=90, wedgeprops={"edgecolor": "white", "linewidth": 2})
    ax1.set_title("Class Distribution (Sessions)")

    # Row counts
    row_counts = df.groupby('Will_Finish').size()
    ax2.bar(labels, row_counts.values, color=colors, alpha=0.85, edgecolor="white")
    for i, v in enumerate(row_counts.values):
        ax2.text(i, v + 200, f"{v:,}", ha="center", fontsize=11)
    ax2.set_ylabel("Number of Training Rows")
    ax2.set_title("Class Distribution (Training Rows)")
    ax2.yaxis.grid(True, alpha=0.3)
    ax2.set_axisbelow(True)

    plt.suptitle("Class Balance in Cleaned Dataset", fontweight="bold", y=1.02)
    plt.tight_layout()

    path = f"{OUT_DIR}/class_distribution.png"
    plt.savefig(path)
    plt.close()
    print(f"  ✓ {path}")


# ── Plot 7: Feature Distributions (Grid with Gaussian Fit) ─────────────────
def plot_feature_distributions(df, df_agg):
    """2×5 grid of all features with histogram + Gaussian fit + p-value."""
    PLOT_FEATURES = [
        'jumpSuccessRate', 'jumpsFailed', 'totalFalls', 'maxFallDistance',
        'distancePerJump', 'avgTimeBetweenJumps', 'totalJumpsAttempted',
        'velocity_magnitude', 'pos_x', 'pos_y'
    ]
    n_cols, n_rows = 2, 5
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(12, 18))
    axes = axes.flatten()

    for idx, feat in enumerate(PLOT_FEATURES):
        ax  = axes[idx]
        col = df_agg[feat].dropna() if feat in df_agg.columns else df[feat].dropna()

        # Histogram
        ax.hist(col, bins=15, density=True, color="#4C72B0", alpha=0.6,
                edgecolor="white", linewidth=0.6, label="Data")

        # Gaussian fit
        mu, sigma = sp_stats.norm.fit(col)
        x = np.linspace(col.min(), col.max(), 200)
        ax.plot(x, sp_stats.norm.pdf(x, mu, sigma),
                color="#C44E52", lw=2, label=f"μ={mu:.2f}, σ={sigma:.2f}")

        # ±1σ shading
        ax.fill_between(x, sp_stats.norm.pdf(x, mu, sigma),
                        where=(x >= mu - sigma) & (x <= mu + sigma),
                        alpha=0.15, color="#C44E52", label="±1σ")

        # p-value (D'Agostino)
        if len(col) >= 20:
            _, pval = sp_stats.normaltest(col)
            verdict = "Normal" if pval > 0.05 else "Not Normal"
            color_p = "#2ca02c" if pval > 0.05 else "#d62728"
            ax.text(0.97, 0.95, f"p = {pval:.2e}\n{verdict}",
                    transform=ax.transAxes, ha="right", va="top",
                    fontsize=8.5, color=color_p,
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=color_p, alpha=0.8))

        ax.set_title(FEATURE_LABELS.get(feat, feat), fontsize=11)
        ax.set_ylabel("Density")
        ax.legend(fontsize=7.5, loc="upper left")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(alpha=0.25)

    plt.suptitle("Feature Distributions with Gaussian Fit (per-session aggregated)",
                 fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()

    path = f"{OUT_DIR}/feature_distributions_gaussian.png"
    plt.savefig(path)
    plt.close()
    print(f"  ✓ {path}")


# ── Plot 8: PCA Skill Score Distribution ────────────────────────────────────
def plot_pca_skill_score(df_agg):
    """Standardised PCA skill score with Gaussian fit, confidence bands, and class rug plot."""
    feat_cols = [f for f in FEATURES if f in df_agg.columns]
    data_clean = df_agg[feat_cols + ['Will_Finish']].dropna()

    if len(data_clean) < 5:
        print("  ⚠ Not enough data points for PCA plot.")
        return

    X      = data_clean[feat_cols].values
    labels = data_clean['Will_Finish'].values

    scaler = StandardScaler()
    X_sc   = scaler.fit_transform(X)
    pca    = PCA(n_components=1)
    scores = pca.fit_transform(X_sc).flatten()
    var_exp = pca.explained_variance_ratio_[0] * 100

    _, pval = sp_stats.normaltest(scores)
    mu, sigma = sp_stats.norm.fit(scores)

    fig, ax = plt.subplots(figsize=(9, 5))

    # Background histogram
    ax.hist(scores, bins=12, density=True,
            color="#4C72B0", alpha=0.45, edgecolor="white", zorder=2)

    # Gaussian fit curve
    x_range = np.linspace(scores.min() - 0.5, scores.max() + 0.5, 300)
    pdf     = sp_stats.norm.pdf(x_range, mu, sigma)
    ax.plot(x_range, pdf, color="#1a1a2e", lw=2.5,
            linestyle="--", label=f"Gaussian Fit (μ={mu:.2f}, σ={sigma:.2f})", zorder=3)

    # ±1σ and ±2σ confidence bands
    for band, alpha, label in [
        (2, 0.10, "±2σ (95.4%)"),
        (1, 0.20, "±1σ (68.3%)"),
    ]:
        ax.fill_between(x_range, pdf,
                        where=(x_range >= mu - band*sigma) & (x_range <= mu + band*sigma),
                        alpha=alpha, color="#4C72B0", label=label, zorder=1)

    # Session rug plot by class
    colors_cls = {0: "#C44E52", 1: "#55A868"}
    for cls, clabel in [(0, "Not Finished"), (1, "Finished")]:
        mask = labels == cls
        ax.scatter(scores[mask], np.zeros(mask.sum()) - 0.01,
                   color=colors_cls[cls], s=80, marker="|",
                   linewidths=2, zorder=4, label=clabel, clip_on=False)

    # p-value annotation
    verdict = "Normal ✓" if pval > 0.05 else "Not Normal ✗"
    col_p   = "#2ca02c" if pval > 0.05 else "#d62728"
    ax.text(0.02, 0.97, f"p = {pval:.3e}  →  {verdict}",
            transform=ax.transAxes, va="top", fontsize=10,
            color=col_p, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=col_p, alpha=0.85))

    ax.set_xlabel(f"Skill Score (PC1, explains {var_exp:.1f}% of variance)")
    ax.set_ylabel("Density")
    ax.set_title("Distribution of PCA-Based Skill Score")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(alpha=0.25)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()

    path = f"{OUT_DIR}/pca_skill_score_gaussian.png"
    plt.savefig(path)
    plt.close()
    print(f"  ✓ {path}")


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not os.path.exists(SQL_PATH):
        print(f"Error: {SQL_PATH} not found.")
        exit(1)

    # Parse the SQL dump once — every plot below works off these two frames
    print("Loading data...")
    df     = preprocess_data(parse_sql_to_df(SQL_PATH))
    df_agg = aggregate_per_session(df)

    models, data = train_models(df)

    print(f"\nGenerating plots → {OUT_DIR}/")
    plot_model_comparison(models, data)
    plot_roc_curves(models, data)
    plot_feature_importance(models, data)
    plot_confusion_matrix(models, data)
    plot_win_probability_over_time(models, df)
    plot_class_distribution(df)
    plot_feature_distributions(df, df_agg)
    plot_pca_skill_score(df_agg)

    print(f"\n✓ All plots saved to ml_pipeline/{OUT_DIR}/")
