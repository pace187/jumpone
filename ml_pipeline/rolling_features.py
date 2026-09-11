"""
rolling_features.py
rates over the last window_s seconds instead of cumulative counters. compute on
the full sorted row stream, before terminal states are removed and before subsampling.
"""

import numpy as np
import pandas as pd

IDLE_STATES = {'Idle', 'AFK', 'Paused'}


def _window_start(ts_ms, width_ms):
    """index of the first row inside the window [t-width, t], for every row."""
    return np.searchsorted(ts_ms, ts_ms - width_ms, side='left')


def _cumsum0(x):
    """prefix sum with a leading 0 so window sums are O(1)."""
    return np.concatenate([[0.0], np.cumsum(np.asarray(x, dtype=float))])


def rolling_for_session(g, window_s):
    """window features for one chronologically sorted session."""
    ts = g['timestamp'].to_numpy()
    i = np.arange(len(g))
    j = _window_start(ts, window_s * 1000)
    n = (i - j + 1).astype(float)
    # early in a session the window is shorter than window_s, so the span is
    # measured per row rather than assumed.
    span_s = np.maximum((ts - ts[j]) / 1000.0, 1e-3)

    out = {}

    # differentiate the counters: sums become rates.
    for src, name in [('totalJumpsAttempted', 'jumps'),
                      ('jumpsFailed', 'fails'),
                      ('totalFalls', 'falls')]:
        c = g[src].to_numpy(dtype=float)
        delta = c[i] - c[j]
        out[f'w_{name}'] = delta
        out[f'w_{name}_per_s'] = delta / span_s

    # jump success within the window. with no attempt the rate is undefined;
    # 0.5 is the neutral value that pushes the model neither way.
    out['w_success'] = np.where(
        out['w_jumps'] > 0,
        (out['w_jumps'] - out['w_fails']) / np.maximum(out['w_jumps'], 1),
        0.5,
    )

    # state and input shares within the window.
    flags = {
        'idle': g['state'].isin(IDLE_STATES).to_numpy(dtype=float),
        'charge': (g['state'] == 'Charging').to_numpy(dtype=float),
        'input': ((g['input_left'] + g['input_right'] + g['input_jump']) > 0).to_numpy(dtype=float),
    }
    for name, arr in flags.items():
        cs = _cumsum0(arr)
        out[f'w_{name}_frac'] = (cs[i + 1] - cs[j]) / n

    # motion within the window: mean and spread via prefix sums.
    for src, name in [('velocity_magnitude', 'vel'), ('pos_y', 'y')]:
        x = g[src].to_numpy(dtype=float)
        cs, cs2 = _cumsum0(x), _cumsum0(x * x)
        mean = (cs[i + 1] - cs[j]) / n
        var = np.maximum((cs2[i + 1] - cs2[j]) / n - mean * mean, 0.0)
        if name == 'vel':
            out['w_vel_mean'] = mean
        out[f'w_{name}_std'] = np.sqrt(var)

    # progress as a rate, not a level. pos_y falls towards the goal, so
    # positive means upward.
    y = g['pos_y'].to_numpy(dtype=float)
    out['w_progress'] = y[j] - y[i]
    out['w_progress_per_s'] = out['w_progress'] / span_s

    # stagnation: seconds since the highest position reached so far.
    best = np.minimum.accumulate(y)
    is_new_best = np.concatenate([[True], best[1:] < best[:-1]])
    t_best = pd.Series(np.where(is_new_best, ts, np.nan)).ffill().to_numpy()
    out['stagnation_s'] = (ts - t_best) / 1000.0

    # backtrack: height currently lost against the best position so far.
    out['w_backtrack'] = np.maximum(y[i] - best[i], 0.0)

    return pd.DataFrame(out, index=g.index)


def add_rolling_features(df, window_s=60):
    """appends the window features. df must be the full raw stream."""
    parts = [rolling_for_session(g.sort_values('timestamp'), window_s)
             for _, g in df.groupby('session_id', sort=False)]
    return df.join(pd.concat(parts))


# --- feature sets ---
# the split is graded because whether a feature counts as behaviour is not
# obvious. w_y_std correlates with pos_y at rho = -0.81 and is mostly a
# positional indicator; any 'behaviour beats position' claim must use
# ROLL_BEHAVIOUR.

ROLL_BEHAVIOUR = [                      # free of positional and motion reference
    'w_jumps_per_s', 'w_fails_per_s', 'w_falls_per_s', 'w_success',
    'w_idle_frac', 'w_charge_frac', 'w_input_frac',
]
ROLL_MOTION = ['w_vel_mean', 'w_vel_std', 'w_y_std']    # close to position, rho(pos_y) up to -0.81
ROLL_PROGRESS = ['w_progress_per_s', 'stagnation_s', 'w_backtrack']

ROLL_PURE = ROLL_BEHAVIOUR + ROLL_MOTION               # 'without absolute position'
ROLL_ALL = ROLL_PURE + ROLL_PROGRESS
