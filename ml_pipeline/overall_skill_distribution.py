"""
overall_skill_distribution.py
pca of the nine measured quantities (section 4.6): variance, loadings,
correlation with duration, and the exposure-normalised variant.
  python3 overall_skill_distribution.py --sql ../telemetry_rows_07092026.sql
"""

import os
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from data_parser import parse_sql_to_df, preprocess_data, aggregate_per_session, add_sql_argument, DEFAULT_SQL

MEASURED = [
    "velocity_magnitude", "jumpSuccessRate", "jumpsFailed", "totalFalls",
    "avgFallDistance", "maxFallDistance", "distancePerJump",
    "avgTimeBetweenJumps", "totalJumpsAttempted",
]

COUNTERS = ["totalJumpsAttempted", "jumpsFailed", "totalFalls"]

NORMALISED_SET = [
    "velocity_magnitude", "jumpSuccessRate", "jumpsFailed", "totalFalls",
    "distancePerJump", "totalJumpsAttempted",
]


def first_component(frame):
    """standardise, pca, first component. returns scores, loadings, explained variance."""
    scaled = StandardScaler().fit_transform(frame)
    pca = PCA(n_components=1).fit(scaled)
    return pca.transform(scaled).flatten(), pca.components_[0], pca.explained_variance_ratio_[0]


def analyze_overall_distribution(sql_path=None):
    print("--- PCA of the nine measured quantities (Section 4.6) ---")

    sql_path = sql_path or DEFAULT_SQL
    if not os.path.exists(sql_path):
        print(f"File not found: {sql_path}. Please place it in the project root.")
        return

    df_raw = parse_sql_to_df(sql_path)
    sizes = df_raw.groupby("session_id").size()
    df_raw = df_raw[~df_raw["session_id"].isin(sizes[sizes < 100].index)]
    df = aggregate_per_session(preprocess_data(df_raw))

    data = df[MEASURED].dropna()
    if len(data) == 0:
        print("Error: No data available for PCA analysis.")
        return
    print(f"{len(data)} sessions, {len(MEASURED)} variables\n")

    duration = df_raw.groupby("session_id")["sessionDuration_sec"].max().reindex(data.index)

    scores, loadings, var = first_component(data)
    print(f"PC1 explains {var * 100:.1f} % of the variance\n")
    print("Loadings on PC1:")
    for f, l in sorted(zip(MEASURED, loadings), key=lambda t: -abs(t[1])):
        print(f"  {f:<22}{l:+.2f}")
    print(f"\nSpearman rho(PC1, session duration) = "
          f"{stats.spearmanr(scores, duration).statistic:+.2f}")

    skew, kurt = stats.skew(scores), stats.kurtosis(scores)
    _, p_value = stats.normaltest(scores)
    print(f"PC1 scores: skewness {skew:+.2f}, kurtosis {kurt:+.2f}, "
          f"D'Agostino p = {p_value:.3f}")

    minutes = duration / 60.0
    normalised = data.copy()
    for c in COUNTERS:
        normalised[c] = normalised[c] / minutes

    print("\nExposure-normalised (counters per minute):")
    for label, cols in [("all nine variables", MEASURED),
                        ("six behavioural variables", NORMALISED_SET)]:
        s, l, _ = first_component(normalised[cols])
        rho = stats.spearmanr(s, duration).statistic
        jsr = dict(zip(cols, l))["jumpSuccessRate"]
        print(f"  {label:<26} rho(PC1, duration) = {rho:+.2f}   "
              f"jumpSuccessRate loading {jsr:+.2f}")


if __name__ == "__main__":
    import argparse
    analyze_overall_distribution(
        add_sql_argument(argparse.ArgumentParser()).parse_args().sql
    )
