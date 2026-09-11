#!/usr/bin/env python3
"""
make_figures.py
figures 1, 2, 3, 4, 6 and 7, written to ../bachelor_arbeit/. figure 5 comes
from make_artifact_figure.py.
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
    """figure 4: why a row-level split does not respect the session."""
    rng = np.random.default_rng(seed)
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.6), sharey=True)

    # protocol A: 20 % of rows, drawn from every session
    is_test = rng.random((n_sessions, n_rows)) < 0.2
    # protocol B: one whole session is the test set (one fold)
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
    """figure 6: auc per feature set within the three populated progress bands."""
    bands = ["Start\n> 6000\n(13 W / 28 L)", "early\n4500–6000\n(13 W / 17 L)",
             "middle\n2000–4500\n(13 W / 9 L)"]
    series = [("$pos\\_y$ alone", [0.635, 0.489, 0.453], GREY),
              ("cumulative, no position", [0.516, 0.520, 0.624], ORANGE),
              ("rolling behavioural", [0.802, 0.819, 0.803], BLUE)]

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
    # legend below the axis; inside the plot it would cover a bar label.
    ax.legend(frameon=False, fontsize=8, ncol=3, loc="upper center",
              bbox_to_anchor=(0.5, -0.22))
    ax.set_title("Prediction with vertical progress held approximately constant",
                 fontsize=9.5, loc="left", pad=10)
    fig.savefig(os.path.join(OUT, "fig_5_5_baender.png"))
    plt.close(fig)


# the nine measured quantities of section 4.6 - deliberately not
# models.FEATURES, which has pos_x/pos_y and lacks the two untrained columns.
MEASURED = ["velocity_magnitude", "jumpSuccessRate", "jumpsFailed", "totalFalls",
            "avgFallDistance", "maxFallDistance", "distancePerJump",
            "avgTimeBetweenJumps", "totalJumpsAttempted"]


def fig_distributions(sql):
    """figure 3: distribution of the measured quantities per session. aggregated
    to one value per session because a normality test on rows rejects at the
    smallest deviation (section 4.6)."""
    warnings.filterwarnings("ignore")
    from scipy import stats
    from data_parser import parse_sql_to_df, preprocess_data, aggregate_per_session

    raw = parse_sql_to_df(sql)
    sizes = raw.groupby("session_id").size()
    raw = raw[~raw.session_id.isin(set(sizes[sizes < 100].index))]
    agg = aggregate_per_session(preprocess_data(raw))

    fig, axes = plt.subplots(3, 3, figsize=(8.2, 6.4))
    for ax, feat in zip(axes.ravel(), MEASURED):
        x = agg[feat].dropna()
        skew = stats.skew(x)
        _, pval = stats.normaltest(x)
        normal = pval > 0.05
        colour = BLUE if normal else ORANGE
        ax.hist(x, bins=12, color=colour, edgecolor="white", linewidth=0.6)
        ax.set_title(feat, fontsize=8.5, pad=4)
        ax.text(0.97, 0.92, f"skew {skew:+.2f}\np = {pval:.3f}", transform=ax.transAxes,
                ha="right", va="top", fontsize=7, color="#444")
        ax.tick_params(labelsize=6.5)
        ax.set_yticks([])

    fig.legend(handles=[Patch(fc=BLUE, label="compatible with a normal distribution (p > 0.05)"),
                        Patch(fc=ORANGE, label="not normally distributed (p ≤ 0.05)")],
               loc="lower center", ncol=2, frameon=False, fontsize=8,
               bbox_to_anchor=(0.5, -0.035))
    fig.suptitle(f"Session-aggregated distributions of the nine measured quantities "
                 f"(n = {len(agg)} sessions)", fontsize=10, x=0.5, y=0.98)
    fig.tight_layout(rect=[0, 0.03, 1, 0.96])
    fig.savefig(os.path.join(OUT, "fig_4_6_1_verteilungen.png"))
    plt.close(fig)


def fig_level(level_ts="../src/scenes/Level.ts"):
    """figure 1: the level with the pos_y axis and the band edges. the tilemap
    is read directly from Level.ts so the figure cannot go stale."""
    import re
    src = open(level_ts).read()
    layers = {}
    for m in re.finditer(r'name:\s*"(\w+)",\s*width:\s*(\d+),\s*height:\s*(\d+),'
                         r'.*?data:\s*\[([0-9,\s]+)\]', src, re.S):
        name, w, h = m.group(1), int(m.group(2)), int(m.group(3))
        vals = [int(v) for v in m.group(4).replace("\n", "").split(",") if v.strip()]
        layers[name] = np.array(vals).reshape(h, w)

    TILE = 64
    h, w = layers["collisionLayer"].shape
    START_Y, GOAL_Y = 6612, -70
    BAND_EDGES = [6000, 4500, 2000, 500]

    fig, ax = plt.subplots(figsize=(3.6, 7.4))
    # tile coordinates to pos_y: row 0 is at the top, pos_y = 0
    extent = [0, w * TILE, h * TILE, 0]
    ax.imshow(np.where(layers["designLayer"] > 0, 1, np.nan), extent=extent,
              cmap=matplotlib.colors.ListedColormap(["#d9dce0"]), interpolation="nearest")
    ax.imshow(np.where(layers["collisionLayer"] > 0, 1, np.nan), extent=extent,
              cmap=matplotlib.colors.ListedColormap(["#5b6570"]), interpolation="nearest")
    ax.imshow(np.where(layers["iceLayer"] > 0, 1, np.nan), extent=extent,
              cmap=matplotlib.colors.ListedColormap(["#7fb3d3"]), interpolation="nearest")

    for layer, colour, label in [("checkpointLayer", ORANGE, "checkpoint"),
                                 ("finishLayer", BLUE, "goal")]:
        ys, xs = np.nonzero(layers[layer])
        ax.scatter((xs + .5) * TILE, (ys + .5) * TILE, s=26, color=colour,
                   zorder=4, label=label, edgecolors="white", linewidths=0.5)

    for edge in BAND_EDGES:
        ax.axhline(edge, color="#b00020", lw=0.9, ls="--", zorder=3)
        ax.text(w * TILE + 90, edge, f"{edge}", fontsize=7, color="#b00020", va="center")

    ax.scatter([w * TILE * 0.17], [START_Y], marker="v", s=60, color="#222",
               zorder=5, label="start")
    ax.set_ylim(h * TILE, GOAL_Y - 200)
    ax.set_xlim(-240, w * TILE)
    ax.set_xticks([])
    ax.set_ylabel("pos_y  (smaller = closer to the goal)", fontsize=8)
    ax.set_yticks([0, 2000, 4000, 6000])
    ax.tick_params(labelsize=7.5)
    for s in ("top", "right", "bottom"):
        ax.spines[s].set_visible(False)
    # arrow left of the level so it covers no platforms
    ax.annotate("", xy=(-150, 400), xytext=(-150, 6300),
                arrowprops=dict(arrowstyle="->", color="#222", lw=1.4))
    ax.text(-195, 3350, "direction of play", rotation=90, fontsize=7.5,
            ha="center", va="center", color="#222")
    ax.legend(frameon=False, fontsize=7.5, loc="lower center",
              bbox_to_anchor=(0.5, -0.075), ncol=3)
    ax.set_title(f"{w} × {h} tiles ({w*TILE:,} × {h*TILE:,} px)", fontsize=9, loc="left", pad=8)
    fig.savefig(os.path.join(OUT, "fig_3_1_1_level.png"))
    plt.close(fig)


def fig_class_distribution():
    """figure 2: class balance at row and session level. the row share misses
    the session share in both directions: below before the cap (the longest run
    is abandoned), above after it (all 13 wins reach 500 rows, only 16 of 28
    losses do)."""
    stages = [
        ("rows\nbefore subsampling", 48_567, 116_981),
        ("rows\nafter 500-row cap", 6_500, 11_298),
        ("sessions", 13, 28),
    ]
    SESSION_SHARE = 13 / 41

    fig, ax = plt.subplots(figsize=(6.8, 2.9))
    y = np.arange(len(stages))[::-1]
    for yi, (label, pos, neg) in zip(y, stages):
        share = pos / (pos + neg)
        ax.barh(yi, share, color=BLUE, edgecolor="white", height=0.55)
        ax.barh(yi, 1 - share, left=share, color="#d5d8dc", edgecolor="white", height=0.55)
        ax.text(share / 2, yi, f"{share:.1%}", ha="center", va="center",
                color="white", fontsize=9, fontweight="bold")
        ax.text(1.012, yi, f"{pos:,} / {pos + neg:,}", va="center", fontsize=7.5, color="#555")

    ax.axvline(SESSION_SHARE, color="#444", lw=1.2, ls="--", zorder=3)
    ax.text(SESSION_SHARE + 0.015, 0.52, f"session-level\nshare {SESSION_SHARE:.1%}",
            ha="left", va="center", fontsize=7.5, color="#444")
    ax.set_yticks(y)
    ax.set_yticklabels([s[0] for s in stages], fontsize=8.5)
    ax.set_xlim(0, 1.16)
    ax.set_xticks(np.arange(0, 1.01, 0.25))
    ax.set_xticklabels([f"{v:.0%}" for v in np.arange(0, 1.01, 0.25)], fontsize=8)
    ax.set_xlabel("share of the positive class (session completed)", fontsize=8.5)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    fig.legend(handles=[Patch(fc=BLUE, label="completed"),
                        Patch(fc="#d5d8dc", label="abandoned")],
               loc="lower center", ncol=2, frameon=False, fontsize=8,
               bbox_to_anchor=(0.5, -0.12))
    ax.set_title("The row-level class balance never matches the session-level one",
                 fontsize=9.5, loc="left", pad=10)
    fig.savefig(os.path.join(OUT, "fig_4_4_1_klassenverteilung.png"))
    plt.close(fig)


def fig_time_course(sql):
    """figure 7: auc by elapsed time within the session."""
    warnings.filterwarnings("ignore")
    import pandas as pd
    from sklearn.model_selection import LeaveOneGroupOut
    from sklearn.metrics import roc_auc_score
    from data_parser import parse_sql_to_df
    from models import make_xgboost, FEATURES, TARGET
    from rolling_features import add_rolling_features, ROLL_BEHAVIOUR

    raw = parse_sql_to_df(sql).sort_values(["session_id", "timestamp"])
    sizes = raw.groupby("session_id").size()
    # only exclusion: sessions without active play (section 4.3).
    raw = raw[~raw.session_id.isin(set(sizes[sizes < 100].index))]
    raw = add_rolling_features(raw, window_s=60)
    # seconds since session start, before terminal states are removed
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
    # the last window has too few sessions and is not interpreted.
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

    counts = ["13 W / 28 L", "13 W / 22 L", "13 W / 18 L", "12 W / 15 L", "5 W / 11 L"]
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
                    help="export for figure 7; without it only the schematic figures are drawn")
    args = ap.parse_args()

    fig_level()
    fig_class_distribution()
    fig_protocols()
    fig_bands()
    print("geschrieben nach bachelor_arbeit/:")
    print("  fig_3_1_1_level.png")
    print("  fig_4_4_1_klassenverteilung.png")
    print("  fig_5_1_protokolle.png")
    print("  fig_5_5_baender.png")
    if os.path.exists(args.sql):
        fig_distributions(args.sql)
        print("  fig_4_6_1_verteilungen.png")
        fig_time_course(args.sql)
        print("  fig_5_7_zeitverlauf.png")
    else:
        print(f"  (figure 7 skipped, {args.sql} not found)")
