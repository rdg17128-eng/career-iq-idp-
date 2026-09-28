import os
import pandas as pd
import json
import joblib
import torch
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments
)
from torch.utils.data import Dataset

class ResumeClassificationDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=512):
        self.texts = list(texts)
        self.labels = list(labels)
        self.tokenizer = tokenizer
        self.max_len = max_len
        
    def __len__(self):
        return len(self.texts)
        
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted', zero_division=0)
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

def main():
    print("Loading classification configuration...")
    splits_dir = r"c:\CareerMind_AI\preprocessing\splits\classification"
    model_dir = r"c:\CareerMind_AI\models\resume_classification"
    
    train_csv = os.path.join(splits_dir, "train.csv")
    val_csv = os.path.join(splits_dir, "val.csv")
    label_map_file = os.path.join(splits_dir, "label_map.json")
    
    if not (os.path.exists(train_csv) and os.path.exists(val_csv) and os.path.exists(label_map_file)):
        print("Error: Preprocessed split files or label map not found. Please run preprocessing first.")
        return
        
    # Ensure save directories exist
    tfidf_dir = os.path.join(model_dir, "tfidf_svm")
    transformer_dir = os.path.join(model_dir, "transformer")
    os.makedirs(tfidf_dir, exist_ok=True)
    os.makedirs(transformer_dir, exist_ok=True)
    
    # Load label mapping
    with open(label_map_file, 'r') as f:
        label_data = json.load(f)
    label_to_id = label_data['label_to_id']
    id_to_label = {int(k): v for k, v in label_data['id_to_label'].items()}
    num_labels = len(label_to_id)
    
    # Save label mapping to central classification model folder
    with open(os.path.join(model_dir, "label_map.json"), "w") as f:
        json.dump(label_data, f, indent=2)
    
    print("Loading datasets...")
    df_train = pd.read_csv(train_csv)
    df_val = pd.read_csv(val_csv)
    
    X_train = df_train['clean_text'].fillna('')
    y_train = df_train['label']
    
    X_val = df_val['clean_text'].fillna('')
    y_val = df_val['label']
    
    # =========================================================================
    # 1. Train TF-IDF + Linear SVM Model
    # =========================================================================
    print("\n--- Training TF-IDF + Linear SVM ---")
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=10000, ngram_range=(1, 2), stop_words='english')),
        ('clf', LinearSVC(C=1.0, random_state=42, dual=False))
    ])
    
    print("Fitting TF-IDF and Linear SVM...")
    pipeline.fit(X_train, y_train)
    
    train_acc = accuracy_score(y_train, pipeline.predict(X_train))
    val_acc = accuracy_score(y_val, pipeline.predict(X_val))
    print(f"SVM Training Accuracy:   {train_acc*100:.2f}%")
    print(f"SVM Validation Accuracy: {val_acc*100:.2f}%")
    
    svm_path = os.path.join(tfidf_dir, "classification_pipeline.joblib")
    print(f"Saving SVM pipeline to {svm_path}...")
    joblib.dump(pipeline, svm_path)
    print("SVM model saved successfully!")
    
    # =========================================================================
    # 2. Train DistilBERT Classifier on GPU
    # =========================================================================
    print("\n--- Training DistilBERT Sequence Classifier ---")
    model_name = "distilbert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=num_labels,
        id2label=id_to_label,
        label2id=label_to_id
    )
    
    # Print CUDA status
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"PyTorch is training on: {device.upper()}")
    
    # Build datasets
    train_dataset = ResumeClassificationDataset(X_train, y_train, tokenizer, max_len=512)
    val_dataset = ResumeClassificationDataset(X_val, y_val, tokenizer, max_len=512)
    
    training_args = TrainingArguments(
        output_dir=os.path.join(transformer_dir, "checkpoints"),
        num_train_epochs=5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        warmup_steps=50,
        weight_decay=0.01,
        logging_steps=20,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        learning_rate=3e-5,
        fp16=True,  # GPU acceleration
        report_to="none"
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics
    )
    
    print("Fine-tuning DistilBERT model...")
    train_result = trainer.train()
    
    print("Evaluating DistilBERT model on validation set...")
    eval_results = trainer.evaluate()
    for k, v in eval_results.items():
        print(f"  {k}: {v}")
        
    print(f"Saving DistilBERT model to {transformer_dir}...")
    trainer.save_model(transformer_dir)
    tokenizer.save_pretrained(transformer_dir)
    
    # Save combined validation metrics
    metrics_summary = {
        "svm_val_accuracy": val_acc,
        "transformer_val_accuracy": eval_results["eval_accuracy"],
        "transformer_val_metrics": eval_results
    }
    with open(os.path.join(model_dir, "training_metrics.json"), "w") as f:
        json.dump(metrics_summary, f, indent=2)
    print("All models trained and saved successfully!")

if __name__ == "__main__":
    main()
