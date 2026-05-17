import os
import shutil
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def main():
    parent_dir = r"d:\Predicitive Maintainence for Electrical Machines - II"
    src_csv = os.path.join(parent_dir, "Python Software", "motor_pdm_final_dataset.csv")
    da_dir = os.path.join(parent_dir, "Data Analysis")

    # Create new folder
    os.makedirs(da_dir, exist_ok=True)
    
    # Copy file to new folder
    dest_csv = os.path.join(da_dir, "motor_pdm_final_dataset.csv")
    if os.path.exists(src_csv) and not os.path.exists(dest_csv):
        shutil.copy2(src_csv, dest_csv)
        print(f"File copied to: {dest_csv}")
    elif not os.path.exists(src_csv):
        print(f"Error: Source file not found at {src_csv}")
        return

    # Load data
    df = pd.read_csv(dest_csv)

    print("\n" + "="*50)
    print("1. SUMMARY STATISTICS BY STATE_LABEL")
    print("="*50)
    
    # Exclude Timestamp from stats
    df_numeric = df.drop(columns=['Timestamp'])
    stats = df_numeric.groupby('State_Label').agg(['mean', 'std', 'min', 'max'])
    
    for col in ['Current(A)', 'VFD_Temp(C)', 'RPM', 'ApparentPower(VA)', 'CoolingEfficiency(C/VA)']:
        if col in stats.columns.levels[0]:
            print(f"\n--- Statistics for {col} ---")
            print(stats[col].to_string())

    print("\n" + "="*50)
    print("2. DATA QUALITY CHECK")
    print("="*50)
    print("Missing values in each column:")
    print(df.isnull().sum().to_string())
    
    # Finding outliers in 'Healthy' data for Current
    healthy_current = df[df['State_Label'] == 0]['Current(A)']
    Q1 = healthy_current.quantile(0.25)
    Q3 = healthy_current.quantile(0.75)
    IQR = Q3 - Q1
    outliers = healthy_current[(healthy_current < (Q1 - 1.5 * IQR)) | (healthy_current > (Q3 + 1.5 * IQR))]
    print(f"\nNumber of outliers in Healthy Current(A) (IQR method): {len(outliers)}")

    # Visualizations
    # a. Correlation Analysis Heatmap
    plt.figure(figsize=(10, 8))
    corr_df = df_numeric.corr()
    sns.heatmap(corr_df, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5)
    plt.title("Correlation Analysis Heatmap")
    plt.tight_layout()
    corr_path = os.path.join(da_dir, "correlation_heatmap.png")
    plt.savefig(corr_path)
    print(f"\nSaved correlation heatmap to {corr_path}")
    plt.close()

    # b. Distribution Visualization (Box Plots)
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    sns.boxplot(ax=axes[0], data=df, x='State_Label', y='Current(A)', palette='Set2')
    axes[0].set_title("Current(A) Distribution by State")
    
    sns.boxplot(ax=axes[1], data=df, x='State_Label', y='VFD_Temp(C)', palette='Set2')
    axes[1].set_title("VFD_Temp(C) Distribution by State")
    
    sns.boxplot(ax=axes[2], data=df, x='State_Label', y='RPM', palette='Set2')
    axes[2].set_title("RPM Distribution by State")
    
    plt.tight_layout()
    box_path = os.path.join(da_dir, "box_plots.png")
    plt.savefig(box_path)
    print(f"Saved box plots to {box_path}")
    plt.close()

    # c. Signature Analysis (Scatter Plots)
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    sns.scatterplot(ax=axes[0], data=df, x='Frequency(Hz)', y='Current(A)', hue='State_Label', palette='bright', alpha=0.7)
    axes[0].set_title("Fault Signature: Frequency vs Current")
    
    sns.scatterplot(ax=axes[1], data=df, x='Frequency(Hz)', y='VFD_Temp(C)', hue='State_Label', palette='bright', alpha=0.7)
    axes[1].set_title("Fault Signature: Frequency vs VFD Temp")
    
    plt.tight_layout()
    sig_path = os.path.join(da_dir, "signature_analysis.png")
    plt.savefig(sig_path)
    print(f"Saved signature analysis scatter plots to {sig_path}")
    plt.close()

    # Make CSV Fruitful (drop Timestamp, handle any NaNs)
    # Re-order so State_Label is first or last.
    df_prepared = df_numeric.dropna()
    fruitful_path = os.path.join(da_dir, "motor_pdm_fruitful.csv")
    df_prepared.to_csv(fruitful_path, index=False)
    print(f"\nPrepared fruitful dataset (no timestamp, no missing values) saved to {fruitful_path}")

if __name__ == "__main__":
    main()
