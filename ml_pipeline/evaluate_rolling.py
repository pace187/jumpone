#!/usr/bin/env python3
"""
evaluate_rolling.py
Vergleicht kumulative gegen rollierende Merkmale unter sessionweiser Validierung.

Beantwortet die Frage, die evaluate_model.py offen laesst: Traegt Spielverhalten
ueberhaupt Information ueber den Sessionausgang, oder kommt alles aus der Position
im Level? Dafuer reicht die Gesamt-AUC nicht - sie ist von pos_y dominiert. Es
braucht die AUC INNERHALB einer Fortschrittsstufe, wo die Position konstant gehalten
ist. Erst dort sieht man, ob ein Merkmalssatz mehr kann als Hoehe ablesen.

Alle Kennzahlen mit Bootstrap-Konfidenzintervall ueber Sessions. Bei 25 Sessions und
8 Gewinnen sind Punktschaetzer ohne Intervall irrefuehrend.

Verwendung:
  python3 evaluate_rolling.py --sql ../telemetry_rows_01092026.sql
  python3 evaluate_rolling.py --window 30 --keep-big
"""

import argparse
import warnings

import numpy as np
import pandas as pd
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.metrics import roc_auc_score

from data_parser import parse_sql_to_df, add_sql_argument
from models import make_xgboost, FEATURES, TARGET
from rolling_features import (
    add_rolling_features, ROLL_BEHAVIOUR, ROLL_MOTION, ROLL_PURE, ROLL_ALL,
)

warnings.filterwarnings("ignore")

# Diese Session stellt allein 31 % des Rohexports und wird in der Arbeit
# ausgeschlossen. --keep-big schaltet den Ausschluss ab (Sensitivitaetsanalyse).
DOMINANT_SESSION = '1774209321205-sgs17rrl7'
MIN_ROWS = 100

CUMULATIVE_BEHAVIOUR = [f for f in FEATURES if f not in ('pos_x', 'pos_y')]

# Fortschrittsstufen in pos_y. Kleinere Werte = weiter oben = naeher am Ziel.
BANDS = [
    ('Start   >6000',    6000,  np.inf),
    ('frueh 4500-6000',  4500,  6000),
    ('Mitte 2000-4500',  2000,  4500),
    ('spaet  500-2000',   500,  2000),
    ('Ziel    <=500',  -np.inf,  500),
]


def load(sql, window_s, max_rows, keep_big, seed):
    df = parse_sql_to_df(sql).sort_values(['session_id', 'timestamp'])

    sizes = df.groupby('session_id').size()
    drop = set(sizes[sizes < MIN_ROWS].index)
    if not keep_big:
        drop.add(DOMINANT_SESSION)
    df = df[~df['session_id'].isin(drop)]

    # Fenstermerkmale auf dem vollen Strom, VOR Label-Filter und Subsampling.
    df = add_rolling_features(df, window_s=window_s)

    outcomes = df.groupby('session_id')['state'].apply(lambda s: int((s == 'Finished').any()))
    df[TARGET] = df['session_id'].map(outcomes)
    df = df[~df['state'].isin(['Finished', 'Quit'])]

    if max_rows:
        df = pd.concat([g.sample(n=min(len(g), max_rows), random_state=seed)
                        for _, g in df.groupby('session_id', sort=False)]).sort_index()
    return df


def out_of_fold(df, feats):
    """Leave-One-Session-Out. Jede Zeile wird von einem Modell bewertet,
    das ihre Session nie gesehen hat."""
    X = df[feats].fillna(0).values
    y = df[TARGET].astype(int).values
    groups = df['session_id'].values
    pred = np.zeros(len(df))
    for train, test in LeaveOneGroupOut().split(X, y, groups):
        model = make_xgboost()
        model.fit(X[train], y[train])
        pred[test] = model.predict_proba(X[test])[:, 1]
    return pred


def per_session(sid, y, p):
    """Eine Zeile je Session: mittlere Gewinnwahrscheinlichkeit ueber alle Zeilen."""
    return (pd.DataFrame({'sid': sid, 'y': y, 'p': p})
            .groupby('sid').agg(y=('y', 'first'), p=('p', 'mean')))


def auc_ci(s, rng, n_boot=3000):
    """Bootstrap ueber Sessions - die Session ist die unabhaengige Einheit."""
    if len(set(s.y)) < 2:
        return np.nan, np.nan, np.nan
    point = roc_auc_score(s.y, s.p)
    draws = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(s), len(s))
        yy = s.y.values[idx]
        if len(set(yy)) > 1:
            draws.append(roc_auc_score(yy, s.p.values[idx]))
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return point, lo, hi


def main():
    ap = argparse.ArgumentParser()
    add_sql_argument(ap)
    ap.add_argument('--window', type=int, default=60, help="Fensterlaenge in Sekunden")
    ap.add_argument('--max-rows', type=int, default=500, help="Zeilen je Session (0 = alle)")
    ap.add_argument('--keep-big', action='store_true', help="dominante Session behalten")
    ap.add_argument('--seed', type=int, default=42)
    args = ap.parse_args()

    df = load(args.sql, args.window, args.max_rows or None, args.keep_big, args.seed)
    y = df[TARGET].astype(int).values
    sid = df['session_id'].values
    posy = df['pos_y'].values
    n_sessions = df['session_id'].nunique()
    n_wins = int(df.groupby('session_id')[TARGET].first().sum())
    rng = np.random.default_rng(args.seed)

    print(f"\n{len(df):,} Zeilen | {n_sessions} Sessions | {n_wins} Gewinne / "
          f"{n_sessions - n_wins} Niederlagen | Fenster {args.window}s")
    print(f"Mehrheitsklasse: {max(n_wins, n_sessions - n_wins)}/{n_sessions} "
          f"= {max(n_wins, n_sessions - n_wins) / n_sessions:.1%}\n")

    sets = {
        'pos_y allein':                ['pos_y'],
        'kumulativ, alle 9':           FEATURES,
        'kumulativ, nur Verhalten':    CUMULATIVE_BEHAVIOUR,
        'rollierend + Bewegung':       ROLL_PURE,
        'rollierend, nur Verhalten':   ROLL_BEHAVIOUR,
        'rollierend, alle':            ROLL_ALL,
    }

    header = f"{'Merkmalssatz':28s}{'k':>3}{'Session-AUC':>13}{'95%-CI':>16}{'richtig':>10}"
    print(header + "   " + "".join(f"{b[0]:>17}" for b in BANDS))
    print("-" * len(header) + "-" * (3 + 17 * len(BANDS)))

    for name, feats in sets.items():
        pred = out_of_fold(df, feats)
        s = per_session(sid, y, pred)
        auc, lo, hi = auc_ci(s, rng)
        correct = int(((s.p > 0.5).astype(int) == s.y).sum())

        cells = ""
        for _, low, high in BANDS:
            mask = (posy >= low) & (posy < high)
            sb = per_session(sid[mask], y[mask], pred[mask])
            cells += f"{roc_auc_score(sb.y, sb.p):>17.3f}" if len(set(sb.y)) > 1 else f"{'-':>17}"

        print(f"{name:28s}{len(feats):>3}{auc:>13.3f}   [{lo:.2f}, {hi:.2f}]"
              f"{correct:>7}/{n_sessions}   {cells}")

    # Wie viele Sessions stuetzen ueberhaupt jedes Band? Ohne diese Zeile sind die
    # Spalten rechts nicht interpretierbar: bei 2 Niederlagen im Band ist die AUC
    # eine Muenze, kein Messwert.
    counts = ""
    for _, low, high in BANDS:
        mask = (posy >= low) & (posy < high)
        sb = pd.DataFrame({'sid': sid[mask], 'y': y[mask]}).groupby('sid').y.first()
        counts += f"{f'{int((sb == 1).sum())}W/{int((sb == 0).sum())}N':>17}"
    print(f"\n{'Sessions je Band':28s}{'':32}{'':10}   {counts}")

    print("\nDie Spalten rechts sind AUC INNERHALB einer Fortschrittsstufe, sessionweise")
    print("gemittelt. Dort ist die Position konstant gehalten - nur hier zeigt sich, ob ein")
    print("Merkmalssatz Verhalten liest oder nur Hoehe. 0.5 = Zufall.")
    print("Baender mit weniger als etwa 5 Sessions je Klasse nicht interpretieren.")


if __name__ == '__main__':
    main()
