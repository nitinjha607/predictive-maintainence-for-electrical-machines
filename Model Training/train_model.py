import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prep_dir = os.path.join(base_dir, "Data Preprocessing")
    out_dir = os.path.join(base_dir, "Model Training")
    os.makedirs(out_dir, exist_ok=True)
    
    train_csv = os.path.join(prep_dir, "X_y_train_scaled.csv")
    test_csv = os.path.join(prep_dir, "X_y_test_scaled.csv")
    
    print(f"Loading training data from {train_csv}...")
    df_train = pd.read_csv(train_csv)
    df_test = pd.read_csv(test_csv)
    
    # Separate features and target
    X_train = df_train.drop(columns=['State_Label'])
    y_train = df_train['State_Label']
    
    X_test = df_test.drop(columns=['State_Label'])
    y_test = df_test['State_Label']
    
    # Initialize Random Forest Classifier
    # RF is exceptionally robust for multi-class structured IoT/sensor datasets
    print("Training Random Forest Classifier on 4 Fault States...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    
    # Predictions
    print("Evaluating model on Test Set...")
    y_pred = rf_model.predict(X_test)
    
    # 1. Accuracy
    acc = accuracy_score(y_test, y_pred)
    print("\n" + "="*50)
    print(f"MODEL ACCURACY: {acc * 100:.2f}%")
    print("="*50)
    
    # 2. Classification Report
    labels_names = ["Healthy", "Phase Unbalance", "Overheat", "Bearing Fault"]
    print("\n--- DETAILED CLASSIFICATION REPORT ---")
    print(classification_report(y_test, y_pred, target_names=labels_names))
    
    # 3. Create Confusion Matrix visualization
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels_names, yticklabels=labels_names)
    plt.ylabel('Actual Truth')
    plt.xlabel('Model Prediction')
    plt.title('Performance Confusion Matrix')
    plt.tight_layout()
    cm_path = os.path.join(out_dir, "confusion_matrix.png")
    plt.savefig(cm_path)
    plt.close()
    
    # Save the trained model
    model_save_path = os.path.join(out_dir, "motor_rf_model.pkl")
    joblib.dump(rf_model, model_save_path)
    print(f"\nModel strictly successfully trained and formally saved to: {model_save_path}")
    print(f"Confusion visualization saved to: {cm_path}")
    
    # Feature Importance Printout to see what physical characteristic mattered most
    importances = rf_model.feature_importances_
    feat_df = pd.DataFrame({"Feature": X_train.columns, "Importance(%)": importances*100})
    feat_df = feat_df.sort_values(by="Importance(%)", ascending=False)
    print("\n--- FEATURE IMPORTANCES ---")
    print(feat_df.to_string(index=False))

if __name__ == "__main__":
    main()
