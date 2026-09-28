import os
import json
import joblib
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from xgboost import XGBClassifier

def main():
    print("Initializing Resume-Job Matching evaluation...")
    
    model_dir = r"c:\CareerMind_AI\models\job_matching"
    test_split_path = os.path.join(model_dir, "preprocessing", "test_split.joblib")
    xgb_path = os.path.join(model_dir, "xgboost", "matching_xgboost.json")
    
    if not (os.path.exists(test_split_path) and os.path.exists(xgb_path)):
        print("Error: Test split features or XGBoost model not found. Please train first.")
        return
        
    # Load test split
    print(f"Loading test split features from {test_split_path}...")
    test_data = joblib.load(test_split_path)
    X_test = test_data["X_test"]
    y_test = test_data["y_test"]
    
    # Load XGBoost model
    print(f"Loading XGBoost model from {xgb_path}...")
    model = XGBClassifier()
    model.load_model(xgb_path)
    
    # Run prediction
    print("Running predictions on test set...")
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]  # positive match probabilities
    
    # Compute metrics
    accuracy = accuracy_score(y_test, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, preds, average='binary', zero_division=0)
    cm = confusion_matrix(y_test, preds).tolist()
    
    print("\nEvaluation Results on Test Set:")
    print(f"  Accuracy:  {accuracy*100:.2f}%")
    print(f"  Precision: {precision*100:.2f}%")
    print(f"  Recall:    {recall*100:.2f}%")
    print(f"  F1-Score:  {f1*100:.2f}%")
    
    # Save metrics.json
    metrics_report = {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "confusion_matrix": cm
    }
    
    metrics_path = os.path.join(model_dir, "metrics.json")
    with open(metrics_path, 'w') as f:
        json.dump(metrics_report, f, indent=2)
        
    print(f"\nMatching evaluation metrics saved to {metrics_path}")

if __name__ == "__main__":
    main()
