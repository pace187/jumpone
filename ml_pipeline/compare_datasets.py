#!/usr/bin/env python3
"""
compare_datasets.py
Vergleicht zwei Telemetrie-Exporte miteinander.

Beantwortet drei Fragen:
  1. Was ist ueberhaupt dazugekommen? (Umfang, Sessions, Klassenverteilung)
  2. Haben sich die Feature-Werte verschoben?
  3. Taugt ein auf A trainiertes Modell fuer die Sessions, die nur in B stehen?

Frage 3 ist der eigentliche Wert: die neuen Sessions sind ein echter Holdout,
den das alte Modell nie gesehen hat. Der zeilenweise Split in train_xgboost.py
kann das nicht leisten, weil dort Zeilen derselben Session in Train und Test
landen.

Verwendung:
  python3 compare_datasets.py ../telemetry_rows.sql ../telemetry_rows_01092026.sql
"""

import argparse
import warnings

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, roc_auc_score

from data_parser import parse_sql_to_df, preprocess_data
from models import make_xgboost, FEATURES, TARGET

warnings.filterwarnings("ignore")

W = 78


def load(path):
    df = preprocess_data(parse_sql_to_df(path))
    return df.dropna(subset=["session_id"])


def session_table(df):
    """Eine Zeile pro Session: Umfang, Ausgang, hoechster erreichter Punkt."""
    return df.groupby("session_id").agg(
        rows=("state", "size"),
        win=(TARGET, "first"),
        min_pos_y=("pos_y", "min"),
    )


# ── 1. Umfang ───────────────────────────────────────────────────────────────
def report_scope(a, b, name_a, name_b):
    print(f"\n{'─'*W}\n  1. UMFANG\n{'─'*W}")
    sa, sb = session_table(a), session_table(b)
    rows = [
        ("Zeilen",            len(a),                     len(b)),
        ("Sessions",          len(sa),                    len(sb)),
        ("davon gewonnen",    int(sa["win"].sum()),       int(sb["win"].sum())),
        ("davon verloren",    int((1 - sa["win"]).sum()), int((1 - sb["win"]).sum())),
    ]
    print(f"  {'':<22}{name_a:>22}{name_b:>22}")
    for label, va, vb in rows:
        print(f"  {label:<22}{va:>22,}{vb:>22,}")

    only_a, only_b = set(sa.index) - set(sb.index), set(sb.index) - set(sa.index)
    print(f"\n  Sessions nur in {name_a}: {len(only_a)}")
    print(f"  Sessions nur in {name_b}: {len(only_b)}")
    print(f"  in beiden Dateien:      {len(set(sa.index) & set(sb.index))}")

    if only_b:
        print(f"\n  Die {len(only_b)} zusaetzlichen Sessions in {name_b}:")
        extra = sb.loc[sorted(only_b)].sort_values("rows", ascending=False)
        print(f"    {'Session-ID':<26}{'Zeilen':>8}{'Ausgang':>10}{'min pos_y':>12}")
        for sid, r in extra.iterrows():
            outcome = "gewonnen" if r["win"] else "verloren"
            print(f"    {sid:<26}{int(r['rows']):>8}{outcome:>10}{r['min_pos_y']:>12.0f}")
    return only_b


# ── 2. Feature-Verschiebung ─────────────────────────────────────────────────
def report_drift(a, b, name_a, name_b):
    """Vergleicht Feature-Mittelwerte auf Session-Ebene, damit lange Sessions
    das Bild nicht dominieren."""
    print(f"\n{'─'*W}\n  2. FEATURE-VERSCHIEBUNG (Mittel ueber Sessions)\n{'─'*W}")
    ma = a.groupby("session_id")[FEATURES].mean().mean()
    mb = b.groupby("session_id")[FEATURES].mean().mean()
    print(f"  {'Feature':<24}{name_a:>16}{name_b:>16}{'Aenderung':>14}")
    for f in FEATURES:
        delta = (mb[f] - ma[f]) / ma[f] * 100 if ma[f] else float("nan")
        arrow = "" if not np.isfinite(delta) or abs(delta) < 10 else ("  <<" if abs(delta) >= 30 else "  <")
        print(f"  {f:<24}{ma[f]:>16.2f}{mb[f]:>16.2f}{delta:>13.1f}%{arrow}")
    print("\n  '<' ab 10% Abweichung, '<<' ab 30%.")


# ── 3. Echter Holdout ───────────────────────────────────────────────────────
def report_holdout(a, b, only_b, name_a, name_b):
    print(f"\n{'─'*W}\n  3. MODELL AUS {name_a} AUF DEN NEUEN SESSIONS\n{'─'*W}")
    if not only_b:
        print(f"  {name_b} enthaelt keine zusaetzlichen Sessions — nichts zu pruefen.")
        return

    held = b[b["session_id"].isin(only_b)]
    y_held = held[TARGET].astype(int)
    if y_held.nunique() < 2:
        only = "gewonnen" if y_held.iloc[0] == 1 else "verloren"
        print(f"  Alle {len(only_b)} neuen Sessions sind '{only}' — AUC nicht berechenbar,")
        print(f"  es wird nur die Trefferquote ausgewiesen.")

    model = make_xgboost()
    model.fit(a[FEATURES].fillna(0), a[TARGET].astype(int))
    p = model.predict_proba(held[FEATURES].fillna(0))[:, 1]

    print(f"  Trainiert auf {len(a):,} Zeilen aus {a['session_id'].nunique()} Sessions ({name_a})")
    print(f"  Geprueft auf  {len(held):,} Zeilen aus {len(only_b)} ungesehenen Sessions\n")
    print(f"  Zeilen-Accuracy : {accuracy_score(y_held, (p >= .5).astype(int)):.3f}")
    if y_held.nunique() > 1:
        print(f"  Zeilen-AUC      : {roc_auc_score(y_held, p):.3f}")

    # Session-Ebene: eine Vorhersage pro Session ist das, was wirklich zaehlt
    per = pd.DataFrame({"session_id": held["session_id"].values, "p": p, "y": y_held.values})
    agg = per.groupby("session_id").agg(p=("p", "mean"), y=("y", "first"))
    hits = int(((agg["p"] >= .5).astype(int) == agg["y"]).sum())
    print(f"  korrekt auf Session-Ebene: {hits}/{len(agg)}\n")
    print(f"    {'Session-ID':<26}{'Vorhersage':>12}{'tatsaechlich':>14}{'':>4}")
    for sid, r in agg.sort_values("p", ascending=False).iterrows():
        truth = "gewonnen" if r["y"] else "verloren"
        mark = "ok" if (r["p"] >= .5) == bool(r["y"]) else "FALSCH"
        print(f"    {sid:<26}{r['p']*100:>11.1f}%{truth:>14}{mark:>8}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("alt", help="aelterer SQL-Export (Referenz)")
    ap.add_argument("neu", help="neuerer SQL-Export")
    args = ap.parse_args()

    name_a = args.alt.split("/")[-1].replace(".sql", "")[:20]
    name_b = args.neu.split("/")[-1].replace(".sql", "")[:20]

    a, b = load(args.alt), load(args.neu)
    only_b = report_scope(a, b, name_a, name_b)
    report_drift(a, b, name_a, name_b)
    report_holdout(a, b, only_b, name_a, name_b)
    print(f"\n{'─'*W}\n")


if __name__ == "__main__":
    main()
