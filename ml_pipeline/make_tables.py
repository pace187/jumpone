#!/usr/bin/env python3
"""
make_tables.py
every table of the thesis from a single data build, as markdown.
  python3 make_tables.py --sql ../telemetry_rows_07092026.sql [--quick]
"""

import argparse
import warnings

import numpy as np
import pandas as pd
from scipy.stats import binomtest
from sklearn.model_selection import train_test_split, LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score, roc_auc_score, brier_score_loss

from data_parser import parse_sql_to_df, preprocess_data, add_sql_argument
from models import (make_xgboost, make_logistic_regression, make_decision_tree,
                    FEATURES, TARGET)
from rolling_features import add_rolling_features, ROLL_BEHAVIOUR, ROLL_PURE, ROLL_ALL

warnings.filterwarnings("ignore")

MIN_ROWS = 100          # section 4.3: no active play below this
MAX_ROWS = 500          # section 4.3: row cap per session
WINDOW = 60             # section 5.6: rolling window length
SEED = 42
N_BOOT = 4000
BOOT_SEED = 0    # own seed, independent of the row draw

CUMULATIVE_BEHAVIOUR = [f for f in FEATURES if f not in ("pos_x", "pos_y")]

BANDS = [("Start > 6000", 6000, np.inf), ("early 4500–6000", 4500, 6000),
         ("middle 2000–4500", 2000, 4500), ("late 500–2000", 500, 2000),
         ("goal ≤ 500", -np.inf, 500)]
WINDOWS = [("0–30 s", 0, 30), ("30–60 s", 30, 60), ("60–120 s", 60, 120),
           ("120–240 s", 120, 240), ("> 240 s", 240, np.inf)]


# ── build ───────────────────────────────────────────────────────────────────
def build(sql, window=WINDOW, max_rows=MAX_ROWS, seed=SEED):
    """the dataset of the thesis. order matters: the rolling features need the
    unbroken row stream, so they come before terminal states are removed and
    before subsampling."""
    raw = parse_sql_to_df(sql).sort_values(["session_id", "timestamp"])
    sizes = raw.groupby("session_id").size()
    raw = raw[~raw.session_id.isin(sizes[sizes < MIN_ROWS].index)]

    raw = add_rolling_features(raw, window_s=window)
    raw["t_sec"] = raw.groupby("session_id")["timestamp"].transform(
        lambda s: (s - s.min()) / 1000)

    outcomes = raw.groupby("session_id")["state"].apply(
        lambda s: int((s == "Finished").any()))
    raw[TARGET] = raw.session_id.map(outcomes)
    full = raw[~raw.state.isin(["Finished", "Quit"])]
    if not max_rows:
        return full
    return pd.concat([g.sample(n=min(len(g), max_rows), random_state=seed)
                      for _, g in full.groupby("session_id", sort=False)]).sort_index()


# ── helpers ─────────────────────────────────────────────────────────────────
def out_of_fold(df, feats, make_model=make_xgboost, group="session_id"):
    X = df[feats].fillna(0).values
    y = df[TARGET].astype(int).values
    g = df[group].values
    pred = np.zeros(len(df))
    for tr, te in LeaveOneGroupOut().split(X, y, g):
        m = make_model()
        m.fit(X[tr], y[tr])
        pred[te] = m.predict_proba(X[te])[:, 1]
    return pred


def per_session(df, pred, mask=None):
    k = np.ones(len(df), bool) if mask is None else mask
    return (pd.DataFrame({"sid": df.session_id.values[k],
                          "y": df[TARGET].astype(int).values[k],
                          "p": pred[k]})
            .groupby("sid").agg(y=("y", "first"), p=("p", "mean")))


def boot_ci(s, rng):
    """bootstrap over sessions - the session is the independent unit. bounds
    fluctuate between runs in the second decimal."""
    draws = []
    for _ in range(N_BOOT):
        i = rng.integers(0, len(s), len(s))
        if len(set(s.y.values[i])) > 1:
            draws.append(roc_auc_score(s.y.values[i], s.p.values[i]))
    return np.percentile(draws, [2.5, 97.5])


def md(rows, header):
    print("| " + " | ".join(header) + " |")
    print("|" + "|".join(["---"] * len(header)) + "|")
    for r in rows:
        print("| " + " | ".join(str(x) for x in r) + " |")
    print()


# ── tables ──────────────────────────────────────────────────────────────────
def dataset_facts(sql, d):
    raw = parse_sql_to_df(sql)
    sizes = raw.groupby("session_id").size()
    small = sizes[sizes < MIN_ROWS]
    kept = raw[~raw.session_id.isin(small.index)]
    term = int(kept.state.isin(["Finished", "Quit"]).sum())
    full = build(sql, max_rows=0)
    s = d.groupby("session_id")[TARGET].first()

    print("## Chapter 4 — dataset\n")
    md([["raw export", f"{len(raw):,} rows", f"{raw.session_id.nunique()} sessions"],
        [f"excluded (< {MIN_ROWS} rows)", f"{small.sum():,} rows ({small.sum()/len(raw):.2%})",
         f"{len(small)} sessions"],
        ["after exclusion", f"{len(kept):,} rows", f"{kept.session_id.nunique()} sessions"],
        ["terminal rows removed", f"{term} rows", "Finished / Quit"],
        ["before subsampling", f"{len(full):,} rows", f"{full[TARGET].mean():.1%} positive"],
        [f"after {MAX_ROWS}-row cap", f"{len(d):,} rows", f"{d[TARGET].mean():.1%} positive"],
        ["session level", f"{int(s.sum())} of {len(s)}", f"{s.mean():.1%} positive"]],
       ["stage", "rows", "note"])

    rows_per = full.groupby("session_id").size()
    dur = parse_sql_to_df(sql).groupby("session_id")["sessionDuration_sec"].max() / 60
    print("Rows per session: completed Ø {:.0f}, abandoned Ø {:.0f}".format(
        rows_per[s[s == 1].index].mean(), rows_per[s[s == 0].index].mean()))
    dd = dur.reindex(s.index)
    print("Median duration: completed {:.1f} min, abandoned {:.1f} min\n".format(
        dd[s == 1].median(), dd[s == 0].median()))

    print("Spearman correlation with elapsed session time (training frame):\n")
    md([[c, f"{pd.Series(d[c].astype(float)).corr(d.sessionDuration_sec.astype(float), method='spearman'):+.3f}"]
        for c in CUMULATIVE_BEHAVIOUR]
       + [["w_y_std vs pos_y", f"{pd.Series(d.w_y_std).corr(pd.Series(d.pos_y), method='spearman'):+.3f}"]],
       ["feature", "ρ"])


def table_5_2_1(d):
    print("## Table 5.2.1 — Protocol A (row-level hold-out)\n")
    X, y = d[FEATURES].fillna(0), d[TARGET].astype(int)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.2,
                                          random_state=SEED, stratify=y)
    sc = StandardScaler()
    a, b = sc.fit_transform(Xtr), sc.transform(Xte)
    rows = [["Majority-class baseline", f"{max(yte.mean(), 1-yte.mean()):.1%}", "—", "0.500"]]
    for name, m, tr, te in [("Logistic Regression", make_logistic_regression(), a, b),
                            ("Decision Tree (depth = 4)", make_decision_tree(), Xtr, Xte),
                            ("XGBoost (30 trees, depth = 3)", make_xgboost(), Xtr, Xte)]:
        m.fit(tr, ytr)
        rows.append([name, f"{m.score(te, yte):.1%}", f"{f1_score(yte, m.predict(te)):.3f}",
                     f"{roc_auc_score(yte, m.predict_proba(te)[:, 1]):.3f}"])
    md(rows, ["Model", "Accuracy", "F1-Score", "AUC-ROC"])
    print(f"Test set {len(yte):,} rows, {yte.mean():.1%} positive.\n")


def tables_5_3_1_and_5_5_2(d, rng):
    """all three tables from the same out-of-fold predictions; no model is
    trained twice, only the grouping changes."""
    n = d.session_id.nunique()
    wins = int(d.groupby("session_id")[TARGET].first().sum())
    base = max(wins, n - wins)
    y = d[TARGET].astype(int).values
    posy = d.pos_y.values
    t = d.t_sec.values

    sets = [("`pos_y` alone (XGBoost)", ["pos_y"], make_xgboost),
            ("All nine features (Logistic Regression)", FEATURES, make_logistic_regression),
            ("All nine features (XGBoost)", FEATURES, make_xgboost),
            ("All nine features (Decision Tree)", FEATURES, make_decision_tree),
            ("Cumulative features without position", CUMULATIVE_BEHAVIOUR, make_xgboost),
            ("Rolling, behavioural only", ROLL_BEHAVIOUR, make_xgboost),
            ("Rolling, including motion measures", ROLL_PURE, make_xgboost),
            ("Rolling, all", ROLL_ALL, make_xgboost)]

    preds, r53, r55, r57 = {}, [], [], []
    r53.append(["Majority-class baseline", "0.500", "—", f"{base}/{n}", "—", "—"])
    for name, feats, mk in sets:
        p = out_of_fold(d, feats, mk)
        preds[name] = p
        s = per_session(d, p)
        lo, hi = boot_ci(s, rng)
        correct = int(((s.p > .5).astype(int) == s.y).sum())
        pval = binomtest(correct, n, base / n, alternative="greater").pvalue
        r53.append([name, f"{roc_auc_score(s.y, s.p):.3f}", f"[{lo:.2f}, {hi:.2f}]",
                    f"{correct}/{n}", f"{pval:.4f}", f"{brier_score_loss(s.y, s.p):.3f}"])

        def band_row(edges, values):
            out = [name]
            for _, lo_, hi_ in edges:
                m = (values >= lo_) & (values < hi_)
                sb = per_session(d, p, m)
                out.append(f"{roc_auc_score(sb.y, sb.p):.3f}" if len(set(sb.y)) > 1 else "—")
            return out
        r55.append(band_row(BANDS, posy))
        r57.append(band_row(WINDOWS, t))

    def counts(edges, values):
        out = ["*Sessions*"]
        for _, lo_, hi_ in edges:
            m = (values >= lo_) & (values < hi_)
            sb = pd.DataFrame({"sid": d.session_id.values[m], "y": y[m]}).groupby("sid").y.first()
            out.append(f"*{int((sb == 1).sum())} W / {int((sb == 0).sum())} L*")
        return out

    print("## Table 5.3.1 — Protocol B (leave-one-session-out)\n")
    md(r53, ["Feature set / model", "Session AUC", "95 % CI", "Sessions correct", "p", "Brier"])

    print("## Table 5.5.2 — AUC within bands of vertical progress\n")
    md(r55 + [counts(BANDS, posy)], ["Feature set"] + [b[0] for b in BANDS])

    print("## Table 5.7.1 — AUC by elapsed time within the session\n")
    md(r57 + [counts(WINDOWS, t)], ["Feature set"] + [w[0] for w in WINDOWS])
    return preds


def table_5_5_1(d):
    print("## Table 5.5.1 — XGBoost feature importance (gain)\n")
    m = make_xgboost()
    m.fit(d[FEATURES].fillna(0).values, d[TARGET].astype(int).values)
    md([[i, f"`{f}`", f"{g*100:.1f} %"]
        for i, (f, g) in enumerate(sorted(zip(FEATURES, m.feature_importances_),
                                          key=lambda t: -t[1]), 1)],
       ["Rank", "Feature", "Gain"])
    print("Fitted on all {:,} training rows, not out-of-fold: these are descriptive\n"
          "weights of the deployed configuration, not a generalisation estimate.\n".format(len(d)))


def section_5_8(sql, d, preds, old_sessions, quick):
    print("## Section 5.8 — robustness\n")
    n = d.session_id.nunique()

    # collection waves
    is_new = (~d.session_id.isin(old_sessions)).astype(int).values
    print("**Collection waves**\n")
    rows = []
    for name in ("All nine features (XGBoost)", "Rolling, behavioural only"):
        s = pd.DataFrame({"sid": d.session_id.values, "y": is_new,
                          "p": preds[name]}).groupby("sid").agg(y=("y", "first"), p=("p", "mean"))
        rows.append([name, "orders sessions by wave", f"{roc_auc_score(s.y, s.p):.3f}"])
    for name, feats in [("All nine features", FEATURES), ("Rolling, behavioural only", ROLL_BEHAVIOUR)]:
        X = d[feats].fillna(0).values
        g = d.session_id.values
        p = np.zeros(len(d))
        for tr, te in LeaveOneGroupOut().split(X, is_new, g):
            m = make_xgboost(); m.fit(X[tr], is_new[tr])
            p[te] = m.predict_proba(X[te])[:, 1]
        s = pd.DataFrame({"sid": g, "y": is_new, "p": p}).groupby("sid").agg(y=("y", "first"), p=("p", "mean"))
        rows.append([name, "trained on wave membership", f"{roc_auc_score(s.y, s.p):.3f}"])
    md(rows, ["Feature set", "Test", "AUC"])

    # protocol B'
    pid = parse_sql_to_df(sql).groupby("session_id")["player_id"].first()
    d = d.copy(); d["pid"] = d.session_id.map(pid)
    print(f"**Player-level generalisation (Protocol B′)** — {d.pid.nunique()} groups\n")
    rows = []
    for name, feats in [("`pos_y` alone", ["pos_y"]), ("All nine features", FEATURES),
                        ("Rolling, behavioural only", ROLL_BEHAVIOUR)]:
        s = per_session(d, out_of_fold(d, feats, group="pid"))
        rows.append([name, f"{roc_auc_score(s.y, s.p):.3f}",
                     f"{int(((s.p > .5).astype(int) == s.y).sum())}/{n}"])
    # post-september sessions only, grouped by player: otherwise the two runs
    # of the same person could land on both sides of the split.
    dn = d[~d.session_id.isin(old_sessions)]
    m = dn.groupby("session_id")[TARGET].first()
    for name, feats in [("`pos_y` alone", ["pos_y"]), ("All nine features", FEATURES),
                        ("Rolling, behavioural only", ROLL_BEHAVIOUR)]:
        s = per_session(dn, out_of_fold(dn, feats, group="pid"))
        rows.append([f"{name} — post-September sessions, leave-one-player-out",
                     f"{roc_auc_score(s.y, s.p):.3f}",
                     f"{int(((s.p > .5).astype(int) == s.y).sum())}/{len(m)}"])
    md(rows, ["Feature set", "Session AUC", "Sessions correct"])

    if quick:
        print("_(window lengths and seed variation skipped: --quick)_\n")
        return

    print("**Further checks** — window length\n")
    rows = []
    for w in (10, 30, 60, 120, 300):
        dw = build(sql, window=w)
        s = per_session(dw, out_of_fold(dw, ROLL_BEHAVIOUR))
        rows.append([f"{w} s", f"{roc_auc_score(s.y, s.p):.3f}"])
    md(rows, ["Window", "Session AUC (rolling, behavioural only)"])

    print("**Further checks** — subsampling seed\n")
    rows = []
    for seed in (42, 7, 123):
        ds = build(sql, seed=seed)
        s = per_session(ds, out_of_fold(ds, FEATURES))
        rows.append([str(seed), f"{roc_auc_score(s.y, s.p):.3f}"])
    md(rows, ["random_state", "Session AUC (all nine features)"])


def main():
    ap = argparse.ArgumentParser()
    add_sql_argument(ap)
    ap.add_argument("--previous-sql", default="../telemetry_rows_01092026.sql",
                    help="older export, defines the first collection wave")
    ap.add_argument("--quick", action="store_true",
                    help="skip window lengths and seeds")
    args = ap.parse_args()

    d = build(args.sql)
    rng = np.random.default_rng(BOOT_SEED)
    try:
        old = set(parse_sql_to_df(args.previous_sql).session_id)
    except Exception:
        old = set()
        print("_(wave check skipped: older export not readable)_\n")

    print(f"\n<!-- generated by make_tables.py, {args.sql}, "
          f"window={WINDOW}s, max_rows={MAX_ROWS}, seed={SEED} -->\n")
    dataset_facts(args.sql, d)
    table_5_2_1(d)
    preds = tables_5_3_1_and_5_5_2(d, rng)
    table_5_5_1(d)
    if old:
        section_5_8(args.sql, d, preds, old, args.quick)


if __name__ == "__main__":
    main()
