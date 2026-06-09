"""
visualize_results.py
Generiert publikationsreife Grafiken für die Bachelorarbeit/Seminararbeit.

Ausgabe: ml_pipeline/plots/
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    confusion_matrix, roc_curve, auc,
    f1_score, ConfusionMatrixDisplay
)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

from data_parser import parse_sql_to_df, preprocess_data

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


# ── Daten laden & Modelle trainieren ────────────────────────────────────────
def load_and_train():
    print("Lade Daten und trainiere Modelle...")
    df_raw = parse_sql_to_df(SQL_PATH)
    df     = preprocess_data(df_raw)[FEATURES + [TARGET]].fillna(0)

    X = df[FEATURES]
    y = df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler        = StandardScaler()
    X_train_sc    = scaler.fit_transform(X_train)
    X_test_sc     = scaler.transform(X_test)

    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train_sc, y_train)

    dt = DecisionTreeClassifier(max_depth=4, random_state=42)
    dt.fit(X_train, y_train)

    model = xgb.XGBClassifier(
        n_estimators=30, max_depth=3,
        learning_rate=0.1, random_state=42, base_score=0.5
    )
    model.fit(X_train, y_train)

    return (lr, dt, model), (X_train, X_test, X_train_sc, X_test_sc, y_train, y_test)


# ── Plot 1: Modellvergleich (Accuracy + F1) ──────────────────────────────────
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
    ax.set_title("Modellvergleich: Accuracy & F1-Score")
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.legend()
    ax.yaxis.grid(True, alpha=0.3)
    ax.set_axisbelow(True)

    path = f"{OUT_DIR}/model_comparison.png"
    plt.savefig(path)
    plt.close()
    print(f"  ✓ {path}")


# ── Plot 2: ROC-Kurven ───────────────────────────────────────────────────────
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

    ax.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5, label="Zufalls-Klassifikator")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC-Kurven – Modellvergleich")
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


# ── Plot 4: Konfusionsmatrix (XGBoost) ──────────────────────────────────────
def plot_confusion_matrix(models, data):
    _, _, xgb_m = models
    _, X_test, _, _, _, y_test = data

    cm = confusion_matrix(y_test, xgb_m.predict(X_test))
    fig, ax = plt.subplots(figsize=(5, 4))
    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["Nicht beendet (0)", "Beendet (1)"]
    )
    disp.plot(ax=ax, colorbar=False, cmap="Blues")
    ax.set_title("Konfusionsmatrix – XGBoost")
    ax.set_xlabel("Vorhergesagte Klasse")
    ax.set_ylabel("Wahre Klasse")
    plt.tight_layout()

    path = f"{OUT_DIR}/confusion_matrix.png"
    plt.savefig(path)
    plt.close()
    print(f"  ✓ {path}")


# ── Plot 5: Win-Probability über Zeit (eine Beispiel-Session) ───────────────
def plot_win_probability_over_time(models, data):
    """Zeigt wie sich die Gewinnwahrscheinlichkeit im Spielverlauf entwickelt."""
    _, _, xgb_m = models
    X_train, X_test, *_ = data
    y_train = data[4]

    df_raw = parse_sql_to_df(SQL_PATH)
    df     = preprocess_data(df_raw).fillna(0)

    # Wähle eine Finished-Session und eine Quit-Session
    finished_sessions = df[df['Will_Finish'] == 1]['session_id'].unique()
    quit_sessions     = df[df['Will_Finish'] == 0]['session_id'].unique()

    if len(finished_sessions) == 0 or len(quit_sessions) == 0:
        print("  ⚠ Nicht genug Sessions für Win-Probability-Plot.")
        return

    fig, ax = plt.subplots(figsize=(10, 5))

    for sid, label, color in [
        (finished_sessions[0], "Beendete Session (Will_Finish=1)", "#55A868"),
        (quit_sessions[0],     "Abgebrochene Session (Will_Finish=0)", "#C44E52"),
    ]:
        session = df[df['session_id'] == sid][FEATURES].fillna(0)
        if len(session) < 10:
            continue
        probs = xgb_m.predict_proba(session)[:, 1]
        # Zeitachse normalisiert auf [0, 100%]
        x = np.linspace(0, 100, len(probs))
        ax.plot(x, probs, label=label, color=color, lw=2, alpha=0.85)
        ax.fill_between(x, probs, alpha=0.1, color=color)

    ax.axhline(0.5, color="gray", lw=1, linestyle="--", alpha=0.6, label="50%-Schwelle")
    ax.set_xlabel("Spielfortschritt (%)")
    ax.set_ylabel("Geschätzte Gewinnwahrscheinlichkeit")
    ax.set_title("Win-Wahrscheinlichkeit im Spielverlauf (XGBoost)")
    ax.set_ylim(0, 1)
    ax.legend()
    ax.grid(alpha=0.3)

    path = f"{OUT_DIR}/win_probability_over_time.png"
    plt.savefig(path)
    plt.close()
    print(f"  ✓ {path}")


# ── Plot 6: Klassenverteilung im Datensatz ───────────────────────────────────
def plot_class_distribution():
    df_raw = parse_sql_to_df(SQL_PATH)
    df     = preprocess_data(df_raw)

    per_session = df.groupby('session_id')['Will_Finish'].first()
    counts = per_session.value_counts().sort_index()
    labels = ["Nicht beendet\n(Quit/Idle)", "Beendet\n(Finished)"]
    colors = ["#C44E52", "#55A868"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # Pie
    ax1.pie(counts, labels=labels, colors=colors, autopct="%1.0f%%",
            startangle=90, wedgeprops={"edgecolor": "white", "linewidth": 2})
    ax1.set_title("Klassenverteilung (Sessions)")

    # Zeilenanzahl
    row_counts = df.groupby('Will_Finish').size()
    ax2.bar(labels, row_counts.values, color=colors, alpha=0.85, edgecolor="white")
    for i, v in enumerate(row_counts.values):
        ax2.text(i, v + 200, f"{v:,}", ha="center", fontsize=11)
    ax2.set_ylabel("Anzahl Trainingszeilen")
    ax2.set_title("Klassenverteilung (Trainingszeilen)")
    ax2.yaxis.grid(True, alpha=0.3)
    ax2.set_axisbelow(True)

    plt.suptitle("Klassenbalance im bereinigten Datensatz", fontweight="bold", y=1.02)
    plt.tight_layout()

    path = f"{OUT_DIR}/class_distribution.png"
    plt.savefig(path)
    plt.close()
    print(f"  ✓ {path}")


# ── Plot 7: Feature-Verteilungen (Grid mit Gaussian-Fit) ───────────────────────────
def plot_feature_distributions():
    """2×5 Grid aller Features mit Histogramm + Gaussian-Fit + p-Wert."""
    from scipy import stats as sp_stats
    from data_parser import aggregate_per_session

    df_raw = parse_sql_to_df(SQL_PATH)
    df     = preprocess_data(df_raw)
    df_agg = aggregate_per_session(df)

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

        # Histogramm
        ax.hist(col, bins=15, density=True, color="#4C72B0", alpha=0.6,
                edgecolor="white", linewidth=0.6, label="Daten")

        # Gaussian-Fit
        mu, sigma = sp_stats.norm.fit(col)
        x = np.linspace(col.min(), col.max(), 200)
        ax.plot(x, sp_stats.norm.pdf(x, mu, sigma),
                color="#C44E52", lw=2, label=f"μ={mu:.2f}, σ={sigma:.2f}")

        # Schraffur: ±1σ
        ax.fill_between(x, sp_stats.norm.pdf(x, mu, sigma),
                        where=(x >= mu - sigma) & (x <= mu + sigma),
                        alpha=0.15, color="#C44E52", label="±1σ")

        # p-Wert (D'Agostino)
        if len(col) >= 20:
            _, pval = sp_stats.normaltest(col)
            verdict = "Normalverteilt" if pval > 0.05 else "Nicht normalverteilt"
            color_p = "#2ca02c" if pval > 0.05 else "#d62728"
            ax.text(0.97, 0.95, f"p = {pval:.2e}\n{verdict}",
                    transform=ax.transAxes, ha="right", va="top",
                    fontsize=8.5, color=color_p,
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=color_p, alpha=0.8))

        ax.set_title(FEATURE_LABELS.get(feat, feat), fontsize=11)
        ax.set_ylabel("Dichte")
        ax.legend(fontsize=7.5, loc="upper left")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(alpha=0.25)

    plt.suptitle("Feature-Verteilungen mit Gaussian-Fit (pro Session aggregiert)",
                 fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()

    path = f"{OUT_DIR}/feature_distributions_gaussian.png"
    plt.savefig(path)
    plt.close()
    print(f"  ✓ {path}")


# ── Plot 8: PCA Skill-Score Verteilung (aufgewertet) ─────────────────────────
def plot_pca_skill_score():
    """Normierter PCA-Skill-Score mit Gaussian-Fit, Konfidenzbändern und Klassen-Markierungen."""
    from scipy import stats as sp_stats
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    from data_parser import aggregate_per_session

    df_raw = parse_sql_to_df(SQL_PATH)
    df     = preprocess_data(df_raw)
    df_agg = aggregate_per_session(df)

    feat_cols = [f for f in FEATURES if f in df_agg.columns]
    data_clean = df_agg[feat_cols + ['Will_Finish']].dropna()

    if len(data_clean) < 5:
        print("  ⚠ Zu wenig Datenpunkte für PCA-Plot.")
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

    # Hintergrund-Histogramm
    ax.hist(scores, bins=12, density=True,
            color="#4C72B0", alpha=0.45, edgecolor="white", zorder=2)

    # Gaussian-Fit-Kurve
    x_range = np.linspace(scores.min() - 0.5, scores.max() + 0.5, 300)
    pdf     = sp_stats.norm.pdf(x_range, mu, sigma)
    ax.plot(x_range, pdf, color="#1a1a2e", lw=2.5,
            linestyle="--", label=f"Gaussian Fit (μ={mu:.2f}, σ={sigma:.2f})", zorder=3)

    # ±1σ und ±2σ Konfidenzbänder
    for band, alpha, label in [
        (2, 0.10, "±2σ (95.4%)"),
        (1, 0.20, "±1σ (68.3%)"),
    ]:
        ax.fill_between(x_range, pdf,
                        where=(x_range >= mu - band*sigma) & (x_range <= mu + band*sigma),
                        alpha=alpha, color="#4C72B0", label=label, zorder=1)

    # Einzelne Sessions als Rugplot + farbige Punkte
    colors_cls = {0: "#C44E52", 1: "#55A868"}
    for cls, clabel in [(0, "Nicht beendet"), (1, "Beendet")]:
        mask = labels == cls
        ax.scatter(scores[mask], np.zeros(mask.sum()) - 0.01,
                   color=colors_cls[cls], s=80, marker="|",
                   linewidths=2, zorder=4, label=clabel, clip_on=False)

    # p-Wert Annotation
    verdict = "Normalverteilt ✓" if pval > 0.05 else "Nicht normalverteilt ✗"
    col_p   = "#2ca02c" if pval > 0.05 else "#d62728"
    ax.text(0.02, 0.97, f"p = {pval:.3e}  →  {verdict}",
            transform=ax.transAxes, va="top", fontsize=10,
            color=col_p, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=col_p, alpha=0.85))

    ax.set_xlabel(f"Skill Score (PC1, erklärt {var_exp:.1f}% der Varianz)")
    ax.set_ylabel("Dichte")
    ax.set_title("Verteilung des PCA-basierten Skill Scores")
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
        print(f"Fehler: {SQL_PATH} nicht gefunden.")
        exit(1)

    models, data = load_and_train()

    print(f"\nGeneriere Plots → {OUT_DIR}/")
    plot_model_comparison(models, data)
    plot_roc_curves(models, data)
    plot_feature_importance(models, data)
    plot_confusion_matrix(models, data)
    plot_win_probability_over_time(models, data)
    plot_class_distribution()
    plot_feature_distributions()
    plot_pca_skill_score()

    print(f"\n✓ Alle Plots gespeichert in ml_pipeline/{OUT_DIR}/")
