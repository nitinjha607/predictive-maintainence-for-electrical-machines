import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def main():
    # Use robust absolute paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(base_dir)
    src_csv = os.path.join(parent_dir, "Data Analysis", "motor_pdm_fruitful.csv")
    
    print(f"Loading data from {src_csv}...")
    try:
        df = pd.read_csv(src_csv)
    except FileNotFoundError:
        print(f"FAILED TO LOAD: File not found exactly at: {src_csv}")
        return
        
    if 'State_Label' not in df.columns:
        print("Error: 'State_Label' not found in dataset")
        return
        
    X = df.drop(columns=['State_Label'])
    y = df['State_Label']
    
    # Stratified Train-Test Split (80% Train, 20% Test)
    print("Splitting dataset 80/20 with stratified classes...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Standardization / Feature Scaling
    print("Standardizing features (fit on train, transform train/test)...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    df_X_train_scaled = pd.DataFrame(X_train_scaled, columns=X.columns)
    df_X_test_scaled = pd.DataFrame(X_test_scaled, columns=X.columns)
    
    df_train_final = pd.concat([df_X_train_scaled, y_train.reset_index(drop=True)], axis=1)
    df_test_final = pd.concat([df_X_test_scaled, y_test.reset_index(drop=True)], axis=1)
    
    train_out_path = os.path.join(base_dir, "X_y_train_scaled.csv")
    test_out_path = os.path.join(base_dir, "X_y_test_scaled.csv")
    
    print("Saving processed CSVs...")
    df_train_final.to_csv(train_out_path, index=False)
    df_test_final.to_csv(test_out_path, index=False)
    
    scaler_path = os.path.join(base_dir, "scaler.pkl")
    joblib.dump(scaler, scaler_path)
    
    print("\n--- Data Preprocessing Operations Complete ---")
    print(f"X_train samples: {len(df_train_final)}")
    print(f"X_test samples: {len(df_test_final)}")
    print(f"Feature Scaler successfully saved to: scaler.pkl")

if __name__ == "__main__":
    main()
