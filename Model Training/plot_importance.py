import os
import pandas as pd
import joblib
import matplotlib.pyplot as plt

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prep_dir = os.path.join(base_dir, "Data Preprocessing")
    out_dir = os.path.join(base_dir, "Model Training")
    
    # Load model
    model_path = os.path.join(out_dir, "motor_rf_model.pkl")
    print(f"Loading model from {model_path}...")
    rf_model = joblib.load(model_path)
    
    # Load train data to get feature names
    train_csv = os.path.join(prep_dir, "X_y_train_scaled.csv")
    print(f"Loading training data to get feature names...")
    df_train = pd.read_csv(train_csv)
    X_train = df_train.drop(columns=['State_Label'])
    
    # Get feature importances
    importances = rf_model.feature_importances_
    
    # Create DataFrame for plotting
    feat_df = pd.DataFrame({
        "Feature": X_train.columns, 
        "Importance": importances
    })
    
    # Sort for better visualization
    feat_df = feat_df.sort_values(by="Importance", ascending=True)
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    
    # Use matplotlib instead of seaborn
    plt.barh(feat_df["Feature"], feat_df["Importance"], color="#1f77b4")
    
    plt.title('Random Forest Feature Importances', fontsize=15, weight='bold')
    plt.xlabel('Relative Importance', fontsize=12)
    plt.ylabel('Features', fontsize=12)
    plt.tight_layout()
    
    # Use the same output directory
    plot_path = os.path.join(out_dir, "feature_importance.png")
    plt.savefig(plot_path, dpi=300)
    plt.close()
    
    print(f"Feature importance bar chart successfully generated at: {plot_path}")

if __name__ == "__main__":
    main()
