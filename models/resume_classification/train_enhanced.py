import os
import sys
import pandas as pd
import json
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import VotingClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

def get_project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def main():
    root = get_project_root()
    splits_dir = os.path.join(root, "preprocessing", "splits", "classification")
    model_dir = os.path.join(root, "models", "resume_classification")
    
    train_csv = os.path.join(splits_dir, "train.csv")
    val_csv = os.path.join(splits_dir, "val.csv")
    test_csv = os.path.join(splits_dir, "test.csv")
    label_map_file = os.path.join(splits_dir, "label_map.json")
    
    df_train = pd.read_csv(train_csv)
    df_val = pd.read_csv(val_csv)
    df_test = pd.read_csv(test_csv)
    
    X_train = df_train['clean_text'].fillna('')
    y_train = df_train['label']
    
    X_val = df_val['clean_text'].fillna('')
    y_val = df_val['label']
    
    X_test = df_test['clean_text'].fillna('')
    y_test = df_test['label']
    
    print(f'Training on {len(X_train)} samples, validating on {len(X_val)}, testing on {len(X_test)}', flush=True)
    
    # 1. Enhanced TF-IDF Vectorizer
    tfidf = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=25000,
        sublinear_tf=True,
        min_df=2,
        strip_accents='unicode'
    )
    
    # 2. Calibrated Linear Classifier
    base_svc = LinearSVC(C=1.0, random_state=42, dual=False)
    calibrated_svc = CalibratedClassifierCV(estimator=base_svc, cv=3)
    
    pipeline = Pipeline([
        ('tfidf', tfidf),
        ('clf', calibrated_svc)
    ])
    
    print('Fitting enhanced classification pipeline...', flush=True)
    pipeline.fit(X_train, y_train)
    
    val_preds = pipeline.predict(X_val)
    val_acc = accuracy_score(y_val, val_preds)
    
    test_preds = pipeline.predict(X_test)
    test_acc = accuracy_score(y_test, test_preds)
    test_p, test_r, test_f1, _ = precision_recall_fscore_support(y_test, test_preds, average='weighted', zero_division=0)
    
    print(f'Enhanced Pipeline Validation Accuracy: {val_acc*100:.2f}%', flush=True)
    print(f'Enhanced Pipeline Test Accuracy:       {test_acc*100:.2f}% (F1: {test_f1*100:.2f}%)', flush=True)
    
    # Save the pipeline
    tfidf_dir = os.path.join(model_dir, "tfidf_svm")
    os.makedirs(tfidf_dir, exist_ok=True)
    svm_path = os.path.join(tfidf_dir, "classification_pipeline.joblib")
    joblib.dump(pipeline, svm_path)
    print(f'Saved enhanced classification pipeline to {svm_path}', flush=True)

if __name__ == '__main__':
    main()
