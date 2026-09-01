import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from data_parser import parse_sql_to_df, preprocess_data, aggregate_per_session, add_sql_argument, DEFAULT_SQL
from models import FEATURES

# FEATURES kommt aus models.py. Der Skill-Score soll denselben Merkmalsraum
# beschreiben wie das ausgelieferte Modell — eine eigene Liste hier wuerde
# unbemerkt veralten, sobald sich der Feature-Satz aendert.

def analyze_overall_distribution(sql_path=None):
    print("--- Overall Dataset Gaussian Analysis (PCA) ---")

    sql_path = sql_path or DEFAULT_SQL
    if not os.path.exists(sql_path):
        print(f"File not found: {sql_path}. Please place it in the project root.")
        return

    df_raw = parse_sql_to_df(sql_path)
    df = preprocess_data(df_raw)
    df = aggregate_per_session(df)

    data = df[FEATURES].dropna()
    
    if len(data) == 0:
        print("Error: No data available for PCA analysis.")
        return
        
    print(f"Extracted {len(data)} valid data points across {len(FEATURES)} features.")
    
    # Step 1: Standardize the data
    # PCA requires variables to be on the same scale (e.g., velocity magnitude might be in 100s, while jumpsFailed is 1s)
    print("Standardizing features...")
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data)
    
    # Step 2: Principal Component Analysis (PCA)
    # This compresses the 10 dimensions into 1 primary "Skill Score" axis that captures the most variance
    print("Running PCA to extract primary 'Skill Score' component...")
    pca = PCA(n_components=1)
    skill_scores = pca.fit_transform(scaled_data).flatten()
    
    variance_explained = pca.explained_variance_ratio_[0] * 100
    print(f"The extracted component explains {variance_explained:.1f}% of the variance in the player behavior.")
    
    # Step 3: Statistical Check on the combined score
    skew = stats.skew(skill_scores)
    kurt = stats.kurtosis(skill_scores)
    
    if len(skill_scores) >= 20:
        stat, p_value = stats.normaltest(skill_scores)
        is_gaussian = p_value > 0.05
        print(f"\nNormality Results:")
        print(f"  Skewness: {skew:.3f} | Kurtosis: {kurt:.3f}")
        print(f"  P-Value: {p_value:.3e} -> {'Gaussian (Normal)' if is_gaussian else 'NOT Gaussian'}")
    
    # Step 4: Visualizing the Result
    print("\nGenerating Gaussian Distribution plot...")
    plt.figure(figsize=(10, 6))
    
    # Plot the histogram as a density curve
    sns.histplot(skill_scores, kde=True, bins=30, stat='density', color='royalblue', label='Actual Data Distribution')
    
    # Fit and plot a perfect "Ideal" Gaussian curve over it for comparison
    x_min, x_max = plt.xlim()
    x = np.linspace(x_min, x_max, 100)
    mu, std = stats.norm.fit(skill_scores)
    p = stats.norm.pdf(x, mu, std)
    plt.plot(x, p, 'k', linewidth=2.5, linestyle='--', label='Ideal Gaussian Fit')
    
    plt.title('Overall Player Skill Score Distribution (PCA Component 1)')
    plt.xlabel('Extracted Skill Score (Standardized deviations from mean)')
    plt.ylabel('Density (Concentration of Players)')
    plt.legend()
    plt.grid(alpha=0.3)
    
    # Save the output image
    output_dir = "gaussian_plots"
    os.makedirs(output_dir, exist_ok=True)
    out_file = f"{output_dir}/overall_skill_distribution.png"
    
    plt.tight_layout()
    plt.savefig(out_file, dpi=300)
    plt.close()
    
    print(f"Plot successfully saved to: ml_pipeline/{out_file}")

if __name__ == "__main__":
    import argparse
    analyze_overall_distribution(
        add_sql_argument(argparse.ArgumentParser()).parse_args().sql
    )
