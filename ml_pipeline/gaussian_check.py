import os
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from data_parser import parse_sql_to_df, preprocess_data, aggregate_per_session

def check_gaussian(df, features):
    print("--- Gaussian Distribution Check ---")
    for feature in features:
        # Drop NaNs and sort out extreme outliers perfectly overlapping for a clean check
        data = df[feature].dropna()
        if len(data) == 0:
            continue
            
        # Skewness and Kurtosis
        skew = stats.skew(data)
        kurt = stats.kurtosis(data)
        
        # D'Agostino's K-squared test (needs >20 samples)
        if len(data) >= 20:
            stat, p_value = stats.normaltest(data)
            is_gaussian = p_value > 0.05
            
            print(f"Feature: {feature}")
            print(f"  Skewness: {skew:.3f}, Kurtosis: {kurt:.3f}")
            print(f"  P-Value: {p_value:.3e} -> {'Gaussian (Normal)' if is_gaussian else 'NOT Gaussian'}")
        else:
            print(f"Feature: {feature} - Not enough data for robust test.")
            
        # Visual plot
        plt.figure(figsize=(10, 4))
        plt.subplot(1, 2, 1)
        sns.histplot(data, kde=True, bins=30)
        plt.title(f'Histogram of {feature}')
        
        plt.subplot(1, 2, 2)
        stats.probplot(data, dist="norm", plot=plt)
        plt.title(f'Q-Q Plot of {feature}')
        
        plt.tight_layout()
        
        # Save plots to checking folder
        output_dir = "gaussian_plots"
        os.makedirs(output_dir, exist_ok=True)
        plt.savefig(f"{output_dir}/{feature}_dist.png")
        plt.close()

if __name__ == "__main__":
    sql_path = "../telemetry_rows.sql"
    if not os.path.exists(sql_path):
        print(f"File not found: {sql_path}")
        exit(1)

    df_raw = parse_sql_to_df(sql_path)
    df = preprocess_data(df_raw)
    df = aggregate_per_session(df)
    
    # Features to analyze
    numerical_features = [
        "velocity_magnitude", "jumpSuccessRate", "jumpsFailed", "totalFalls",
        "avgFallDistance", "maxFallDistance", "distancePerJump", 
        "avgTimeBetweenJumps", "totalJumpsAttempted"
    ]
    
    check_gaussian(df, numerical_features)
    print("Check complete. Plots saved in 'ml_pipeline/gaussian_plots'.")
