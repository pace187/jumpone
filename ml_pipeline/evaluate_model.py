#!/usr/bin/env python3
"""
evaluate_model.py
Bewertet das Modell, ohne etwas zu exportieren.

train_xgboost.py ueberschreibt bei jedem Lauf src/scenes/WinPredictor.ts und kennt
nur den zeilenweisen Split. Dieses Skript ist die gefahrlose Variante zum Vergleichen
von Konfigurationen und liefert zusaetzlich die session-weise Bewertung.

Warum zwei Bewertungsarten:
  zeilenweise   - train_test_split ueber Zeilen. Zeilen derselben Session landen in
                  Train UND Test, das Modell kann Sessions auswendig lernen. Die Zahl
                  ist damit optimistisch, aber vergleichbar mit dem bisherigen Stand.
  session-weise - Leave-One-Session-Out. Jede Session wird einmal komplett aus dem
                  Training gehalten. Das ist die Leistung auf einem UNBEKANNTEN
                  Spieler und die Zahl, die zaehlt.

Verwendung:
  python3 evaluate_model.py                  # ohne Subsampling
  python3 evaluate_model.py --max-rows 500   # max. 500 Zeilen je Session
"""

import argparse
import warnings

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

from data_parser import parse_sql_to_df, preprocess_data, add_sql_argument
from models import (
    make_logistic_regression, make_decision_tree, make_xgboost,
    FEATURES, TARGET,
)

warnings.filterwarnings("ignore")

W = 78


# ── zeilenweise ─────────────────────────────────────────────────────────────
def eval_rowwise(df):
    """Wie train_xgboost.py: 80/20 ueber Zeilen, ohne Ruecksicht auf Sessions."""
    d = df[FEATURES + [TARGET]].fillna(0)
    X_tr, X_te, y_tr, y_te = train_test_split(
        d[FEATURES], d[TARGET].astype(int), test_size=0.2, random_state=42
    )
    sc = StandardScaler()
    X_tr_sc, X_te_sc = sc.fit_transform(X_tr), sc.transform(X_te)

    print(f"\n  ZEILENWEISER SPLIT  ({len(X_tr):,} Train / {len(X_te):,} Test)")
    print(f"  {'Modell':<24}{'Accuracy':>10}{'F1':>10}{'AUC':>10}")
    for name, model, a, b in [
        ("Logistic Regression", make_logistic_regression(), X_tr_sc, X_te_sc),
        ("Decision Tree",       make_decision_tree(),       X_tr,    X_te),
        ("XGBoost",             make_xgboost(),             X_tr,    X_te),
    ]:
        model.fit(a, y_tr)
        p = model.predict_proba(b)[:, 1]
        print(f"  {name:<24}{model.score(b, y_te):>10.3f}"
              f"{f1_score(y_te, model.predict(b), zero_division=0):>10.3f}"
              f"{roc_auc_score(y_te, p):>10.3f}")


# ── session-weise ───────────────────────────────────────────────────────────
def eval_sessionwise(df, group_col="session_id"):
    """Leave-One-Group-Out. Bei ~25 Gruppen deutlich stabiler als
    StratifiedGroupKFold(5), wo schon die Fold-Aufteilung die AUC um mehrere
    Zehntel verschiebt.

    group_col='player_id' haelt alle Laeufe einer Person zurueck. Nur so misst
    man die Leistung auf einem UNBEKANNTEN Spieler: bleibt ein anderer Lauf
    derselben Person im Training, kann das Modell die Person wiedererkennen
    statt Spielverhalten zu verstehen.
    """
    X = df[FEATURES].fillna(0).values
    y = df[TARGET].astype(int).values
    g = df[group_col].values

    rows = []
    for tr, te in LeaveOneGroupOut().split(X, y, g):
        m = make_xgboost()
        m.fit(X[tr], y[tr])
        p = m.predict_proba(X[te])[:, 1]
        rows.append((g[te][0], y[te][0], p.mean(),
                     accuracy_score(y[te], (p >= .5).astype(int))))
    r = pd.DataFrame(rows, columns=["session", "truth", "p", "row_acc"])

    n = len(r)
    unit = "Sessions" if group_col == "session_id" else "Spieler"

    hits = int(((r["p"] >= .5).astype(int) == r["truth"]).sum())
    majority = int(max(r["truth"].sum(), n - r["truth"].sum()))

    print(f"\n  {unit.upper()}-WEISE (Leave-One-Out ueber {group_col}, {n} Folds)")
    print(f"  {'Session-Level AUC':<24}{roc_auc_score(r['truth'], r['p']):>10.3f}")
    print(f"  {'Zeilen-Accuracy':<24}{r['row_acc'].mean():>10.3f}")
    print(f"  {f'korrekte {unit}':<24}{f'{hits}/{n}':>10}")
    print(f"  {'Mehrheitsklasse (Basis)':<24}{f'{majority}/{n}':>10}"
          f"   <- muss geschlagen werden")
    if hits <= majority:
        print(f"\n  ACHTUNG: Das Modell schlaegt die triviale Mehrheitsklasse nicht.")
    return r


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--max-rows", type=int, default=0,
                    help="max. Zeilen je Session (0 = kein Subsampling)")
    ap.add_argument("--per-session", action="store_true",
                    help="Vorhersage je Session einzeln auflisten")
    ap.add_argument("--group-by", choices=["session", "player"], default="session",
                    help="Einheit der Kreuzvalidierung. 'player' haelt alle Laeufe "
                         "einer Person zurueck und misst damit die Leistung auf "
                         "einem unbekannten Spieler (braucht player_id im Export)")
    add_sql_argument(ap)
    args = ap.parse_args()

    df = preprocess_data(parse_sql_to_df(args.sql),
                         max_rows_per_session=args.max_rows or None)
    df = df.dropna(subset=["session_id"])

    label = f"--max-rows {args.max_rows}" if args.max_rows else "ohne Subsampling"
    print(f"\n{'─'*W}")
    print(f"  {label}   |   {len(df):,} Zeilen   |   "
          f"{df['session_id'].nunique()} Sessions")
    print(f"{'─'*W}")

    group_col = "player_id" if args.group_by == "player" else "session_id"
    if group_col == "player_id":
        if "player_id" not in df.columns or df["player_id"].isna().all():
            print("  Hinweis: Der Export enthaelt keine player_id (Daten von vor der "
                  "Umstellung).\n  Es wird nach Session gruppiert.")
            group_col = "session_id"
        else:
            missing = df["player_id"].isna().sum()
            if missing:
                print(f"  Hinweis: {missing:,} Zeilen ohne player_id werden fuer die "
                      f"spielerweise Auswertung uebersprungen.")
                df = df[df["player_id"].notna()]

    eval_rowwise(df)
    r = eval_sessionwise(df, group_col)

    if args.per_session:
        print(f"\n  {'Session-ID':<26}{'Vorhersage':>12}{'tatsaechlich':>14}{'':>8}")
        for _, row in r.sort_values("p", ascending=False).iterrows():
            truth = "gewonnen" if row["truth"] else "verloren"
            mark = "ok" if (row["p"] >= .5) == bool(row["truth"]) else "FALSCH"
            print(f"  {row['session']:<26}{row['p']*100:>11.1f}%{truth:>14}{mark:>8}")

    print(f"\n{'─'*W}\n")


if __name__ == "__main__":
    main()
