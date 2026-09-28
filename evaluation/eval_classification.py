import os
import pandas as pd
import json
import joblib
import torch
import numpy as np
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support, confusion_matrix
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def softmax(x):
    e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e_x / e_x.sum(axis=-1, keepdims=True)

def main():
    print("Loading model and test dataset for evaluation...")
    
    model_dir = r"c:\CareerMind_AI\models\resume_classification"
    splits_dir = r"c:\CareerMind_AI\preprocessing\splits\classification"
    test_csv = os.path.join(splits_dir, "test.csv")
    
    svm_path = os.path.join(model_dir, "tfidf_svm", "classification_pipeline.joblib")
    transformer_dir = os.path.join(model_dir, "transformer")
    label_map_file = os.path.join(model_dir, "label_map.json")
    
    if not (os.path.exists(svm_path) and os.path.exists(transformer_dir) and os.path.exists(test_csv)):
        print("Error: Models or test dataset not found. Please train models first.")
        return
        
    # Load label map
    with open(label_map_file, 'r') as f:
        label_data = json.load(f)
    id_to_label = {int(k): v for k, v in label_data['id_to_label'].items()}
    num_labels = len(id_to_label)
    
    # Load test data
    df_test = pd.read_csv(test_csv)
    print(f"Loaded test dataset with {len(df_test)} samples.")
    X_test = df_test['clean_text'].fillna('').tolist()
    y_test = df_test['label'].tolist()
    
    # -------------------------------------------------------------------------
    # 1. TF-IDF + SVM Evaluation
    # -------------------------------------------------------------------------
    print("\nEvaluating TF-IDF + Linear SVM model...")
    svm_pipeline = joblib.load(svm_path)
    svm_preds = svm_pipeline.predict(X_test)
    
    svm_decision = svm_pipeline.decision_function(X_test)
    svm_probs = softmax(svm_decision)
    
    svm_acc = accuracy_score(y_test, svm_preds)
    svm_p, svm_r, svm_f1, _ = precision_recall_fscore_support(y_test, svm_preds, average='weighted', zero_division=0)
    svm_cm = confusion_matrix(y_test, svm_preds).tolist()
    
    print(f"SVM Test Accuracy: {svm_acc*100:.2f}% | F1-Score: {svm_f1*100:.2f}%")
    
    # -------------------------------------------------------------------------
    # 2. DistilBERT Evaluation
    # -------------------------------------------------------------------------
    print("\nEvaluating DistilBERT model on GPU...")
    tokenizer = AutoTokenizer.from_pretrained(transformer_dir)
    model = AutoModelForSequenceClassification.from_pretrained(transformer_dir)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    
    bert_probs_list = []
    bert_preds = []
    
    # Run in batches to avoid GPU OOM
    batch_size = 16
    with torch.no_grad():
        for i in range(0, len(X_test), batch_size):
            batch_texts = X_test[i:i+batch_size]
            encodings = tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors='pt'
            ).to(device)
            
            outputs = model(**encodings)
            logits = outputs.logits.cpu().numpy()
            probs = softmax(logits)
            
            bert_probs_list.append(probs)
            preds = np.argmax(probs, axis=-1)
            bert_preds.extend(preds.tolist())
            
    bert_probs = np.vstack(bert_probs_list)
    
    bert_acc = accuracy_score(y_test, bert_preds)
    bert_p, bert_r, bert_f1, _ = precision_recall_fscore_support(y_test, bert_preds, average='weighted', zero_division=0)
    bert_cm = confusion_matrix(y_test, bert_preds).tolist()
    
    print(f"DistilBERT Test Accuracy: {bert_acc*100:.2f}% | F1-Score: {bert_f1*100:.2f}%")
    
    # -------------------------------------------------------------------------
    # 3. Hybrid Ensemble Evaluation (Soft Voting)
    # -------------------------------------------------------------------------
    print("\nEvaluating Hybrid Ensemble (Soft Voting)...")
    # Equal weighting soft voting
    ensemble_probs = 0.5 * svm_probs + 0.5 * bert_probs
    ensemble_preds = np.argmax(ensemble_probs, axis=-1).tolist()
    
    ens_acc = accuracy_score(y_test, ensemble_preds)
    ens_p, ens_r, ens_f1, _ = precision_recall_fscore_support(y_test, ensemble_preds, average='weighted', zero_division=0)
    ens_cm = confusion_matrix(y_test, ensemble_preds).tolist()
    
    print(f"Ensemble Test Accuracy: {ens_acc*100:.2f}% | F1-Score: {ens_f1*100:.2f}%")
    
    # Compare and save metrics to metrics.json
    metrics_report = {
        "svm": {
            "accuracy": svm_acc,
            "precision": svm_p,
            "recall": svm_r,
            "f1": svm_f1,
            "confusion_matrix": svm_cm
        },
        "transformer": {
            "accuracy": bert_acc,
            "precision": bert_p,
            "recall": bert_r,
            "f1": bert_f1,
            "confusion_matrix": bert_cm
        },
        "ensemble": {
            "accuracy": ens_acc,
            "precision": ens_p,
            "recall": ens_r,
            "f1": ens_f1,
            "confusion_matrix": ens_cm
        }
    }
    
    metrics_path = os.path.join(model_dir, "metrics.json")
    with open(metrics_path, 'w') as f:
        json.dump(metrics_report, f, indent=2)
        
    print(f"\nFinal comparative metrics saved to {metrics_path}")
    
    # Save optimal config metadata to ensemble directory
    ensemble_dir = os.path.join(model_dir, "ensemble")
    os.makedirs(ensemble_dir, exist_ok=True)
    
    # Select best model based on F1-score
    models_scores = {
        "svm": svm_f1,
        "transformer": bert_f1,
        "ensemble": ens_f1
    }
    best_model = max(models_scores, key=models_scores.get)
    print(f"Optimal Model Strategy selected: {best_model.upper()} (F1: {models_scores[best_model]*100:.2f}%)")
    
    ensemble_meta = {
        "best_model_strategy": best_model,
        "svm_weight": 0.5,
        "transformer_weight": 0.5,
        "validation_scores": models_scores
    }
    with open(os.path.join(ensemble_dir, "ensemble_config.json"), 'w') as f:
        json.dump(ensemble_meta, f, indent=2)

if __name__ == "__main__":
    main()
