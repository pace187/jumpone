#!/usr/bin/env python3
"""
make_figures.py
Erzeugt die Abbildungen fuer Kapitel 5, die keine Neuberechnung brauchen.

Abbildung 5.1  Protokoll A gegen Protokoll B (rein schematisch)
Abbildung 5.5  AUC innerhalb der Fortschrittsbaender (Zahlen aus evaluate_rolling.py)

Ausgabe nach ../bachelor_arbeit/. Farben sind fuer Farbfehlsichtigkeit und
Graustufendruck gewaehlt: unterschiedliche Helligkeit, kein Rot-Gruen-Paar.
"""

import argparse
import os
import warnings

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

OUT = os.path.join(os.path.dirname(__file__), "..", "bachelor_arbeit")
TRAIN, TEST = "#c9ccd1", "#1f4e79"
GREY, ORANGE, BLUE = "#9aa0a6", "#c07c39", "#1f4e79"

plt.rcParams.update({
    "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 200, "savefig.bbox": "tight",
})


def fig_protocols(n_sessions=20, n_rows=26, seed=3):
    """Warum ein zeilenweiser Split die Session nicht respektiert."""
    rng = np.random.default_rng(seed)
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.6), sharey=True)

    # Protokoll A: 20 % der Zeilen ueberall, quer durch alle Sessions
    is_test = rng.random((n_sessions, n_rows)) < 0.2
    # Protokoll B: eine ganze Session ist Test (ein Fold von 40)
    held_out = 11
    for ax, mask, title, sub in [
        (axes[0], is_test, "Protocol A — row-level hold-out",
         "test rows drawn from every session"),
        (axes[1], np.arange(n_sessions)[:, None] == held_out,
         "Protocol B — leave-one-session-out",
         "one entire session held out per fold"),
    ]:
        m = np.broadcast_to(mask, (n_sessions, n_rows))
        for s in range(n_sessions):
            for r in range(n_rows):
                ax.plot(r, s, "s", ms=3.4,
                        color=TEST if m[s, r] else TRAIN, mec="none")
        ax.set_title(title, fontsize=9.5, pad=9, loc="left")
        ax.text(0, -2.6, sub, fontsize=8, color="#555")
        ax.set_xlabel("telemetry rows within a session →", fontsize=8)
        ax.set_xticks([]); ax.set_yticks([])
        ax.set_xlim(-1.5, n_rows + 0.5); ax.set_ylim(n_sessions + 0.5, -4)
        ax.spines["left"].set_visible(False); ax.spines["bottom"].set_visible(False)

    axes[0].set_ylabel("sessions", fontsize=8)
    fig.legend(handles=[Patch(fc=TRAIN, label="training"),
                        Patch(fc=TEST, label="test")],
               loc="lower center", ncol=2, frameon=False, bbox_to_anchor=(0.5, -0.06))
    fig.savefig(os.path.join(OUT, "fig_5_1_protokolle.png"))
    plt.close(fig)


def fig_bands():
    """AUC je Merkmalssatz innerhalb der drei besetzten Fortschrittsbaender."""
    bands = ["Start\n> 6000\n(13 W / 27 L)", "early\n4500–6000\n(13 W / 16 L)",
             "middle\n2000–4500\n(13 W / 8 L)"]
    series = [("$pos\\_y$ alone", [0.658, 0.462, 0.519], GREY),
              ("cumulative, no position", [0.467, 0.519, 0.663], ORANGE),
              ("rolling behavioural", [0.769, 0.803, 0.769], BLUE)]

    fig, ax = plt.subplots(figsize=(6.4, 3.5))
    x = np.arange(len(bands)); w = 0.26
    for i, (label, vals, c) in enumerate(series):
        off = (i - 1) * w
        ax.bar(x + off, vals, w, label=label, color=c,
               edgecolor="white", linewidth=0.6)
        for xi, v in zip(x + off, vals):
            ax.text(xi, v + 0.012, f"{v:.2f}", ha="center", fontsize=7.5, color="#333")

    ax.axhline(0.5, color="#444", lw=1, ls="--", zorder=0)
    ax.text(-0.62, 0.515, "chance", fontsize=7.5, color="#444", va="bottom")
    ax.set_xticks(x); ax.set_xticklabels(bands, fontsize=8)
    ax.set_ylabel("session-level AUC within band")
    ax.set_ylim(0, 0.88); ax.set_yticks(np.arange(0, 0.9, 0.2))
    ax.set_xlim(-0.65, len(bands) - 0.35)
    # Legende unter die Achse: im Diagramm selbst ist kein Platz, ohne einen
    # Balkenwert zu verdecken.
    ax.legend(frameon=False, fontsize=8, ncol=3, loc="upper center",
              bbox_to_anchor=(0.5, -0.22))
    ax.set_title("Prediction with vertical progress held approximately constant",
                 fontsize=9.5, loc="left", pad=10)
    fig.savefig(os.path.join(OUT, "fig_5_5_baender.png"))
    plt.close(fig)


def fig_time_course(sql):
    """AUC nach verstrichener Spielzeit. Rechnet selbst, weil die Zeitfenster-
    Auswertung sonst nirgends reproduzierbar abgelegt waere."""
    warnings.filterwarnings("ignore")
    import pandas as pd
    from sklearn.model_selection import LeaveOneGroupOut
    from sklearn.metrics import roc_auc_score
    from data_parser import parse_sql_to_df
    from models import make_xgboost, FEATURES, TARGET
    from rolling_features import add_rolling_features, ROLL_BEHAVIOUR

    BIG = "1774209321205-sgs17rrl7"
    raw = parse_sql_to_df(sql).sort_values(["session_id", "timestamp"])
    sizes = raw.groupby("session_id").size()
    raw = raw[~raw.session_id.isin(set(sizes[sizes < 100].index) | {BIG})]
    raw = add_rolling_features(raw, window_s=60)
    # Sekunden seit Sessionbeginn, vor dem Entfernen der Endzustaende
    raw["t_sec"] = raw.groupby("session_id")["timestamp"].transform(lambda s: (s - s.min()) / 1000)
    outc = raw.groupby("session_id")["state"].apply(lambda s: int((s == "Finished").any()))
    raw[TARGET] = raw.session_id.map(outc)
    raw = raw[~raw.state.isin(["Finished", "Quit"])]
    d = pd.concat([g.sample(n=min(len(g), 500), random_state=42)
                   for _, g in raw.groupby("session_id", sort=False)]).sort_index()

    y = d[TARGET].astype(int).values
    groups = d.session_id.values
    t_sec = d.t_sec.values

    def out_of_fold(feats):
        X = d[feats].fillna(0).values
        pred = np.zeros(len(d))
        for tr, te in LeaveOneGroupOut().split(X, y, groups):
            m = make_xgboost(); m.fit(X[tr], y[tr])
            pred[te] = m.predict_proba(X[te])[:, 1]
        return pred

    sets = [("$pos\\_y$ alone", ["pos_y"], GREY),
            ("all nine features", FEATURES, ORANGE),
            ("rolling behavioural", ROLL_BEHAVIOUR, BLUE)]
    windows = [("0–30 s", 0, 30), ("30–60 s", 30, 60), ("60–120 s", 60, 120),
               ("120–240 s", 120, 240), ("> 240 s", 240, np.inf)]

    fig, ax = plt.subplots(figsize=(6.6, 3.8))
    x = np.arange(len(windows))
    # Letztes Fenster hat nur 5 Gewinne / 10 Niederlagen und wird nicht interpretiert.
    ax.axvspan(len(windows) - 1.5, len(windows) - 0.5, color="#000", alpha=0.045, zorder=0)
    ax.text(len(windows) - 1, 0.955, "too few sessions\nto interpret",
            ha="center", va="top", fontsize=7.5, color="#666")

    print(f"{'feature set':<22}" + "".join(f"{w[0]:>12}" for w in windows))
    for label, feats, colour in sets:
        pred = out_of_fold(feats)
        vals = []
        for _, lo, hi in windows:
            m = (t_sec >= lo) & (t_sec < hi)
            s = (pd.DataFrame({"sid": groups[m], "y": y[m], "p": pred[m]})
                 .groupby("sid").agg(y=("y", "first"), p=("p", "mean")))
            vals.append(roc_auc_score(s.y, s.p) if len(set(s.y)) > 1 else np.nan)
        ax.plot(x[:-1], vals[:-1], "-o", color=colour, lw=1.8, ms=5, label=label)
        ax.plot(x[-2:], vals[-2:], ":o", color=colour, lw=1.4, ms=5, alpha=0.55)
        print(f"{label:<22}" + "".join(f"{v:>12.3f}" for v in vals))

    counts = ["13 W / 27 L", "13 W / 22 L", "13 W / 17 L", "12 W / 14 L", "5 W / 10 L"]
    ax.axhline(0.5, color="#444", lw=1, ls="--", zorder=0)
    ax.text(-0.42, 0.515, "chance", fontsize=7.5, color="#444")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{w[0]}\n{c}" for w, c in zip(windows, counts)], fontsize=8)
    ax.set_xlim(-0.45, len(windows) - 0.55)
    ax.set_ylim(0.2, 1.0)
    ax.set_ylabel("session-level AUC within window")
    ax.set_xlabel("elapsed time within the session", fontsize=8.5)
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    ax.set_title("The prediction is usable from the first half-minute",
                 fontsize=9.5, loc="left", pad=10)
    fig.savefig(os.path.join(OUT, "fig_5_7_zeitverlauf.png"))
    plt.close(fig)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sql", default="../telemetry_rows_07092026.sql",
                    help="Export fuer Abbildung 5.7; ohne Datei werden nur 5.1 und 5.5 erzeugt")
    args = ap.parse_args()

    fig_protocols()
    fig_bands()
    print("geschrieben nach bachelor_arbeit/:")
    print("  fig_5_1_protokolle.png")
    print("  fig_5_5_baender.png")
    if os.path.exists(args.sql):
        fig_time_course(args.sql)
        print("  fig_5_7_zeitverlauf.png")
    else:
        print(f"  (5.7 uebersprungen, {args.sql} nicht gefunden)")
