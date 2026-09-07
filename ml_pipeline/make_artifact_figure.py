#!/usr/bin/env python3
"""
make_artifact_figure.py
Erzeugt Abbildung 5.4: wie eine einzige Pause das alte Modell ausser Kraft setzt.

Die Abbildung braucht das Modell von VOR der Korrektur, weil das heutige
avgTimeBetweenJumps gar nicht mehr kennt. Es wird aus dem Git-Verlauf geholt
(Commit 72bf8b9 vom 10. Juni 2026) und mit node ueber die Zeilen einer
betroffenen Session laufen gelassen. Nichts daran ist rekonstruiert.

Voraussetzungen: node im PATH, git-Repository vorhanden.
Aufruf: python3 make_artifact_figure.py [--sql ../telemetry_rows_01092026.sql]
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import warnings

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from data_parser import parse_sql_to_df

warnings.filterwarnings("ignore")

COMMIT = "72bf8b9"                       # letzte Fassung mit avgTimeBetweenJumps
MODEL_PATH = "src/scenes/WinPredictor.ts"
THRESHOLD = 1940.9534                    # Wurzelverzweigung in 21 von 23 Baeumen
# Diese Session ueberschreitet die Schwelle nach 3.0 von 5.8 Minuten und zeigt
# deshalb ein sauberes Vorher und Nachher. Alle zwoelf Sessions, die die
# Schwelle je ueberschritten haben, wurden abgebrochen.
SESSION = "1778351252932-8ckl1zh31"
# Merkmalsreihenfolge des alten Modells (aus dem Kopf der generierten Datei)
ORDER = ["jumpSuccessRate", "jumpsFailed", "totalFalls", "maxFallDistance",
         "distancePerJump", "avgTimeBetweenJumps", "totalJumpsAttempted",
         "velocity_magnitude", "pos_x", "pos_y"]

RUNNER = """
const fs = require('fs');
eval(fs.readFileSync(process.argv[2], 'utf8').replace(/export\\s+/g, ''));
const rows = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
// score() liefert bei einem Klassifikator [P(verloren), P(gewonnen)] und hat die
// Sigmoid bereits angewandt. Der damalige Wrapper hat sie ein zweites Mal
// angewandt und deshalb NaN geliefert - hier wird korrekt der letzte Eintrag
// genommen, damit die Abbildung zeigt, was das Modell gemeint hat.
const out = rows.map(r => { const s = score(r);
    return Array.isArray(s) ? s[s.length - 1] : 1 / (1 + Math.exp(-s)); });
fs.writeFileSync(process.argv[4], JSON.stringify(out));
"""


def score_with_old_model(X, repo_root):
    """Holt das alte Modell aus git und bewertet die Zeilen mit node."""
    js = subprocess.run(["git", "-C", repo_root, "show", f"{COMMIT}:{MODEL_PATH}"],
                        capture_output=True, text=True, check=True).stdout
    with tempfile.TemporaryDirectory() as tmp:
        f_model = os.path.join(tmp, "model.js")
        f_rows, f_out = os.path.join(tmp, "rows.json"), os.path.join(tmp, "out.json")
        open(f_model, "w").write(js.replace("export ", ""))
        json.dump(X, open(f_rows, "w"))
        open(os.path.join(tmp, "run.js"), "w").write(RUNNER)
        subprocess.run(["node", os.path.join(tmp, "run.js"), f_model, f_rows, f_out],
                       check=True, capture_output=True)
        return np.array(json.load(open(f_out)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sql", default="../telemetry_rows_01092026.sql")
    ap.add_argument("--out", default="../bachelor_arbeit/fig_5_4_pausen_artefakt.png")
    args = ap.parse_args()
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    df = parse_sql_to_df(args.sql).sort_values(["session_id", "timestamp"])
    g = df[df.session_id == SESSION]
    if g.empty:
        sys.exit(f"Session {SESSION} nicht im Export {args.sql}")

    t = (g.timestamp.to_numpy() - g.timestamp.min()) / 60000.0      # Minuten
    atbj, posy = g.avgTimeBetweenJumps.to_numpy(), g.pos_y.to_numpy()
    p = score_with_old_model(g[ORDER].fillna(0).values.tolist(), root)
    c = int(np.argmax(atbj >= THRESHOLD))                            # Umschlagpunkt

    BLUE, ORANGE, GREY, RED = "#1f4e79", "#c07c39", "#9aa0a6", "#b00020"
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False,
                         "axes.spines.right": False, "figure.dpi": 200,
                         "savefig.bbox": "tight"})
    fig, ax = plt.subplots(3, 1, figsize=(6.8, 6.0), sharex=True,
                           gridspec_kw={"hspace": 0.16})
    for a in ax:
        a.axvspan(t[c], t[-1], color=RED, alpha=0.05, zorder=0)
        a.axvline(t[c], color=RED, lw=1.1, ls="--", zorder=1)

    ax[0].plot(t, atbj, color=ORANGE, lw=1.4)
    ax[0].axhline(THRESHOLD, color=GREY, lw=1, ls=":")
    ax[0].text(0.05, THRESHOLD * 1.08, f"model threshold {THRESHOLD:.2f} ms",
               fontsize=7.5, color="#555")
    ax[0].set_ylabel("avgTimeBetween-\nJumps (ms)", fontsize=8)
    ax[0].annotate(f"{atbj[c-1]:.0f} → {atbj[c]:.0f} ms\nacross one pause",
                   xy=(t[c], atbj[c]), xytext=(t[c] + 0.42, atbj[c] * 0.45),
                   fontsize=8, color=RED,
                   arrowprops=dict(arrowstyle="->", color=RED, lw=0.9))

    ax[1].plot(t, posy, color=GREY, lw=1.4)
    ax[1].invert_yaxis()
    ax[1].set_ylabel("pos_y\n(smaller = closer\nto the goal)", fontsize=8)
    ax[1].text(t[-1] - 0.05, posy.min(), "the player keeps climbing",
               ha="right", va="bottom", fontsize=7.5, color="#555")

    ax[2].plot(t, p * 100, color=BLUE, lw=1.5)
    ax[2].set_ylim(0, 100)
    ax[2].set_ylabel("win probability\nshown in game (%)", fontsize=8)
    ax[2].set_xlabel("time within the session (minutes)", fontsize=8.5)
    ax[2].text(t[c] * 0.5, 82, f"mean {p[:c].mean()*100:.0f} %", ha="center",
               fontsize=8.5, color=BLUE)
    ax[2].text((t[c] + t[-1]) / 2, 82,
               f"mean {p[c:].mean()*100:.0f} % — everything else ignored",
               ha="center", fontsize=8.5, color=RED)

    ax[0].set_title("A single pause disables the model for the rest of the run",
                    fontsize=10.5, loc="left", pad=10)
    fig.text(0.5, -0.03,
             f"Session {SESSION} (abandoned), scored with the model version of "
             f"10 June 2026 (commit {COMMIT}), which still used avgTimeBetweenJumps.\n"
             f"In 21 of its 23 trees that feature formed the root split. All twelve "
             f"sessions that ever crossed the threshold were abandoned.",
             ha="center", fontsize=7.3, color="#555")
    fig.savefig(args.out)
    print(f"{args.out}\n  Umschlag bei Minute {t[c]:.1f} von {t[-1]:.1f}"
          f" | davor Ø {p[:c].mean()*100:.1f} % | danach Ø {p[c:].mean()*100:.1f} %")


if __name__ == "__main__":
    main()
