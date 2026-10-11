# Resume Domain Classification

## Overview
Automated multi-class categorization of resumes across 24 distinct industrial occupational categories using an ensemble of TF-IDF Linear SVM and a fine-tuned DistilBERT sequence classifier.

## Dataset Information
- **Original Dataset Location:** `C:\CareerMind_AI\datasets\resume_classification_dataset\Resume\Resume.csv`
- **Total Records:** 2,484 resumes
- **Target Categories (24):** `ACCOUNTANT`, `ADVOCATE`, `AGRICULTURE`, `APPAREL`, `ARTS`, `AUTOMOBILE`, `AVIATION`, `BANKING`, `BPO`, `BUSINESS-DEVELOPMENT`, `CHEF`, `CONSTRUCTION`, `CONSULTANT`, `DESIGNER`, `DIGITAL-MEDIA`, `ENGINEERING`, `FINANCE`, `FITNESS`, `HEALTHCARE`, `HR`, `INFORMATION-TECHNOLOGY`, `PUBLIC-RELATIONS`, `SALES`, `TEACHER`.

## Preprocessing & Splitting
- **Script:** `preprocessing/preprocess_classification.py`
- **Cleaning:** Text normalization, whitespace collapsing, newline removal.
- **Split Scheme:** Stratified 80/10/10 split on Category labels (Seed: 42).
  - Train: 1,986 samples
  - Validation: 248 samples
  - Test: 249 samples
- **Data Leakage Prevention:** TF-IDF vectorizer vocabulary is fitted strictly on the training partition.

## Model Architecture & Training
- **Model A:** TF-IDF (`max_features=10000`, n-gram 1-2) + `LinearSVC(C=1.0)`
- **Model B:** `distilbert-base-uncased` fine-tuned for 5 epochs with AdamW (`lr=3e-5`).
- **Model C (Ensemble):** Soft-voting mechanism combining calibrated SVM decision scores and DistilBERT softmax probabilities.
- **Training Script:** `training/train_classification.py`
- **Evaluation Script:** `evaluation/evaluate_classification.py`
- **Testing Script:** `testing/test_classification.py`

## Performance Metrics (Untouched Test Split)
- **Linear SVM:** Accuracy: **70.68%** | Weighted F1: **69.80%**
- **DistilBERT:** Accuracy: **87.55%** | Weighted F1: **87.21%**
- **Hybrid Ensemble:** Accuracy: **88.35%** | Weighted F1: **87.64%**

## Saved Artifacts
Stored in `saved_model/` and root directory:
- `tfidf_svm/classification_pipeline.joblib`
- `transformer/model.safetensors`, `transformer/config.json`, `transformer/tokenizer.json`
- `ensemble/ensemble_config.json`
- `label_map.json`

## Inference Usage
```python
from models.resume_classification.inference import ResumeClassifier

classifier = ResumeClassifier()
result = classifier.predict("Experienced Python backend developer with Django, PostgreSQL, and AWS.")
print(result)
```
