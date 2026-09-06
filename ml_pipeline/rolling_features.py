"""
rolling_features.py
Rollierende Fenstermerkmale als Gegenstueck zu den kumulativen Zaehlern.

Warum es diese Datei gibt: die Merkmale in models.FEATURES sind ueberwiegend
kumulative Zaehler ueber die gesamte Session. Sie wachsen per Konstruktion mit der
Zeit und sind damit vor allem Uhren, keine Verhaltensmasse. Gemessen auf dem Export
vom 1.9.2026 (Spearman gegen sessionDuration_sec):

    totalJumpsAttempted  +0.957      distancePerJump     +0.150
    jumpsFailed          +0.945      jumpSuccessRate     +0.056
    totalFalls           +0.830      velocity_magnitude  +0.020
    maxFallDistance      +0.826

Vier der sieben Verhaltensmerkmale sind also nahezu perfekte Stellvertreter fuer die
verstrichene Zeit. Ein Modell, das damit den Sessionausgang vorhersagt, liest ab, wie
lange gespielt wurde - nicht, wie gut.

Die Merkmale hier beschreiben stattdessen ein gleitendes Zeitfenster: Raten statt
Summen, Anteile statt Gesamtzahlen. Sie wachsen nicht mit der Spieldauer.

WARNUNG zur Verwendung: Die Merkmale muessen auf dem VOLLSTAENDIGEN, chronologisch
sortierten Zeilenstrom berechnet werden - vor dem Entfernen der Endzustaende und vor
dem Subsampling. Sonst sind die Fenster loechrig und die Raten falsch.
"""

import numpy as np
import pandas as pd

IDLE_STATES = {'Idle', 'AFK', 'Paused'}


def _window_start(ts_ms, width_ms):
    """Index der ersten Zeile im Fenster [t-width, t] fuer jede Zeile."""
    return np.searchsorted(ts_ms, ts_ms - width_ms, side='left')


def _cumsum0(x):
    """Praefixsumme mit fuehrender 0, damit Fenstersummen O(1) sind."""
    return np.concatenate([[0.0], np.cumsum(np.asarray(x, dtype=float))])


def rolling_for_session(g, window_s):
    """Berechnet die Fenstermerkmale fuer EINE chronologisch sortierte Session."""
    ts = g['timestamp'].to_numpy()
    i = np.arange(len(g))
    j = _window_start(ts, window_s * 1000)
    n = (i - j + 1).astype(float)
    # Bei kurzen Sessions ist das Fenster am Anfang kuerzer als window_s. Die
    # tatsaechliche Spanne wird deshalb pro Zeile gemessen, nicht angenommen.
    span_s = np.maximum((ts - ts[j]) / 1000.0, 1e-3)

    out = {}

    # Kumulative Zaehler differenzieren: aus Summen werden Raten.
    for src, name in [('totalJumpsAttempted', 'jumps'),
                      ('jumpsFailed', 'fails'),
                      ('totalFalls', 'falls')]:
        c = g[src].to_numpy(dtype=float)
        delta = c[i] - c[j]
        out[f'w_{name}'] = delta
        out[f'w_{name}_per_s'] = delta / span_s

    # Sprungerfolg IM FENSTER. Ohne Sprungversuch im Fenster ist die Quote
    # undefiniert; 0.5 ist der neutrale Wert, der das Modell nicht in eine
    # Richtung schiebt.
    out['w_success'] = np.where(
        out['w_jumps'] > 0,
        (out['w_jumps'] - out['w_fails']) / np.maximum(out['w_jumps'], 1),
        0.5,
    )

    # Zustands- und Eingabeanteile im Fenster.
    flags = {
        'idle': g['state'].isin(IDLE_STATES).to_numpy(dtype=float),
        'charge': (g['state'] == 'Charging').to_numpy(dtype=float),
        'input': ((g['input_left'] + g['input_right'] + g['input_jump']) > 0).to_numpy(dtype=float),
    }
    for name, arr in flags.items():
        cs = _cumsum0(arr)
        out[f'w_{name}_frac'] = (cs[i + 1] - cs[j]) / n

    # Bewegung im Fenster: Mittel und Streuung ueber Praefixsummen.
    for src, name in [('velocity_magnitude', 'vel'), ('pos_y', 'y')]:
        x = g[src].to_numpy(dtype=float)
        cs, cs2 = _cumsum0(x), _cumsum0(x * x)
        mean = (cs[i + 1] - cs[j]) / n
        var = np.maximum((cs2[i + 1] - cs2[j]) / n - mean * mean, 0.0)
        if name == 'vel':
            out['w_vel_mean'] = mean
        out[f'w_{name}_std'] = np.sqrt(var)

    # Fortschritt als RATE, nicht als Niveau. pos_y faellt Richtung Ziel,
    # positive Werte bedeuten also Aufstieg.
    y = g['pos_y'].to_numpy(dtype=float)
    out['w_progress'] = y[j] - y[i]
    out['w_progress_per_s'] = out['w_progress'] / span_s

    # Stagnation: Sekunden seit der bisher hoechsten erreichten Position.
    best = np.minimum.accumulate(y)
    is_new_best = np.concatenate([[True], best[1:] < best[:-1]])
    t_best = pd.Series(np.where(is_new_best, ts, np.nan)).ffill().to_numpy()
    out['stagnation_s'] = (ts - t_best) / 1000.0

    # Rueckschritt: aktuell verlorene Hoehe gegenueber dem bisherigen Bestwert.
    out['w_backtrack'] = np.maximum(y[i] - best[i], 0.0)

    return pd.DataFrame(out, index=g.index)


def add_rolling_features(df, window_s=60):
    """Haengt die Fenstermerkmale an. df muss der volle Rohstrom sein."""
    parts = [rolling_for_session(g.sort_values('timestamp'), window_s)
             for _, g in df.groupby('session_id', sort=False)]
    return df.join(pd.concat(parts))


# --- Merkmalssaetze -------------------------------------------------------
# Die Aufteilung ist bewusst gestuft, weil die Zugehoerigkeit eines Merkmals zu
# "Verhalten" nicht selbstverstaendlich ist. w_y_std korreliert mit rho = -0.82
# gegen pos_y und ist damit ueberwiegend ein Positionsindikator, kein Koennensmass.
# Wer "Verhalten schlaegt Position" behaupten will, muss ROLL_BEHAVIOUR benutzen.

ROLL_BEHAVIOUR = [                      # frei von Positions- und Bewegungsbezug
    'w_jumps_per_s', 'w_fails_per_s', 'w_falls_per_s', 'w_success',
    'w_idle_frac', 'w_charge_frac', 'w_input_frac',
]
ROLL_MOTION = ['w_vel_mean', 'w_vel_std', 'w_y_std']    # positionsnah, rho(pos_y) bis -0.82
ROLL_PROGRESS = ['w_progress_per_s', 'stagnation_s', 'w_backtrack']

ROLL_PURE = ROLL_BEHAVIOUR + ROLL_MOTION               # "ohne absolute Position"
ROLL_ALL = ROLL_PURE + ROLL_PROGRESS
