#!/usr/bin/env python3
"""
session_states.py
Zustandsverteilung je Session.

Zeigt fuer jede Session, wie sich ihre Telemetriezeilen auf die Spielzustaende
verteilen. Nuetzlich, um Sessions zu beurteilen, bevor man sie aus dem Datensatz
entfernt: eine hohe Gesamtzeilenzahl sagt noch nichts darueber aus, ob es sich um
aktives Spiel oder um Herumstehen handelt.

Liest den Rohexport OHNE preprocess_data, damit die Endzustaende 'Finished' und
'Quit' sichtbar bleiben — die werden vor dem Training entfernt und tauchen in
aufbereiteten Daten nicht mehr auf.

Verwendung:
  python3 session_states.py                    # Prozentwerte
  python3 session_states.py --absolute         # absolute Zeilenzahlen
  python3 session_states.py --csv tabelle.csv  # zusaetzlich als CSV speichern
"""

import argparse
import warnings

import pandas as pd

from data_parser import parse_sql_to_df, add_sql_argument

warnings.filterwarnings("ignore")

# Reihenfolge der Spalten: aktives Spiel zuerst, dann Untaetigkeit, dann Endzustaende.
STATE_ORDER = ["Jumping", "Falling", "Charging", "Running",
               "Idle", "AFK", "Paused", "Finished", "Quit"]
SHORT = {"Jumping": "Jump", "Falling": "Fall", "Charging": "Charg",
         "Running": "Run", "Idle": "Idle", "AFK": "AFK",
         "Paused": "Paus", "Finished": "Fin", "Quit": "Quit"}


def build_table(df, absolute=False):
    counts = (df.groupby(["session_id", "state"]).size()
                .unstack(fill_value=0))

    # Nur bekannte Zustaende, in fester Reihenfolge; unbekannte hinten anhaengen,
    # damit ein neuer Zustand im Spiel hier nicht stillschweigend verschwindet.
    known = [s for s in STATE_ORDER if s in counts.columns]
    extra = [c for c in counts.columns if c not in STATE_ORDER]
    if extra:
        print(f"  Hinweis: unbekannte Zustaende im Export: {', '.join(map(str, extra))}")
    counts = counts[known + extra]

    total = counts.sum(axis=1)
    table = counts if absolute else counts.div(total, axis=0) * 100
    table.insert(0, "rows", total)
    table.insert(1, "win", counts.get("Finished", pd.Series(0, index=counts.index)).gt(0).astype(int))
    return table.sort_values("rows", ascending=False)


def render(table, absolute):
    state_cols = [c for c in table.columns if c not in ("rows", "win")]
    head = f"  {'Session-ID':<25}{'Zeilen':>8}{'Ergebnis':>10}"
    head += "".join(f"{SHORT.get(c, c):>8}" for c in state_cols)
    print(f"\n{head}\n  {'-' * (len(head) - 2)}")

    for sid, r in table.iterrows():
        line = f"  {sid:<25}{int(r['rows']):>8,}{'gewonnen' if r['win'] else 'verloren':>10}"
        for c in state_cols:
            v = r[c]
            line += f"{int(v):>8,}" if absolute else (f"{v:>7.1f}%" if v > 0 else f"{'-':>8}")
        print(line)

    # Gesamtzeile: Anteile ueber alle Zeilen, nicht Mittel der Session-Anteile —
    # sonst zaehlen kurze und lange Sessions gleich viel.
    print(f"  {'-' * (len(head) - 2)}")
    tot = table["rows"].sum()
    gewonnen = int(table["win"].sum())
    line = f"  {'GESAMT':<25}{int(tot):>8,}{f'{gewonnen}/{len(table)}':>10}"
    for c in state_cols:
        s = (table[c] * table["rows"] / 100).sum() if not absolute else table[c].sum()
        line += f"{int(s):>8,}" if absolute else f"{s / tot * 100:>7.1f}%"
    print(line)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--absolute", action="store_true",
                    help="absolute Zeilenzahlen statt Prozent")
    ap.add_argument("--csv", metavar="PFAD",
                    help="Tabelle zusaetzlich als CSV speichern")
    add_sql_argument(ap)
    args = ap.parse_args()

    df = parse_sql_to_df(args.sql)
    table = build_table(df, args.absolute)

    print(f"\n  {len(table)} Sessions, {int(table['rows'].sum()):,} Zeilen aus {args.sql}")
    render(table, args.absolute)

    if args.csv:
        table.round(2).to_csv(args.csv)
        print(f"\n  CSV geschrieben: {args.csv}")
    print()


if __name__ == "__main__":
    main()
