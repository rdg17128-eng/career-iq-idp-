# Resume–Job Matching Engine

## Overview
Predicts candidate-to-job opening fitment probabilities using dense semantic text representations from Sentence-BERT paired with a gradient boosted decision tree (XGBoost).

## Dataset Information
- **Original Dataset Location:** `C:\CareerMind_AI\datasets\job_matching_dataset\all_job_post.csv` paired with `Resume.csv`.
- **Total Source Jobs:** 1,167 postings
- **Total Candidate Resumes:** 2,484 resumes
- **Generated Pairs:** 8,000 pairs (50% positive matches, 50% negative matches) across shared industrial domains: `HR`, `INFORMATION-TECHNOLOGY`, `SALES`, `FINANCE`, `BUSINESS-DEVELOPMENT`.

## Preprocessing & Feature Engineering
- **Script:** `training/train_matching.py`
- **Leakage Prevention:** Resumes and jobs are stratified into Train (80%), Val (10%), and Test (10%) *before* cartesian pairing.
- **Pairs:**
  - Train: 6,000 pairs
  - Validation: 1,000 pairs
  - Test: 1,000 pairs
- **Feature Representations:**
  1. Cosine similarity between SBERT resume and job embeddings (`all-MiniLM-L6-v2`)
  2. Skill overlap ratio (`job_skill_set` matched in resume text)
  3. Absolute difference vector: `|E_res - E_job|` (384 dimensions)
  4. Element-wise product: `E_res * E_job` (384 dimensions)
  - Total feature vector size: 770 dimensions.

## Training & Evaluation
- **Classifier:** XGBoost (`max_depth=5`, `learning_rate=0.1`, `n_estimators=150`, `early_stopping_rounds=15`).
- **Evaluation Script:** `evaluation/evaluate_matching.py`

## Performance Metrics (Untouched Test Split)
- **Accuracy:** **82.70%**
- **Precision:** **81.38%**
- **Recall:** **84.80%**
- **F1-Score:** **83.06%**
- **Confusion Matrix:** `[[403, 97], [76, 424]]`

## Saved Artifacts
Stored in `saved_model/` and root directory:
- `xgboost/matching_xgboost.json`
- `sentence_transformer/config.json`
- `preprocessing/test_split.joblib`

## Inference Usage
```python
from models.job_matching.inference import ResumeJobMatcher

matcher = ResumeJobMatcher()
res = matcher.predict(
    resume_text="Senior data scientist with expertise in Python, PyTorch, SQL, and Machine Learning.",
    job_description="Seeking a Senior Machine Learning Engineer with strong Python and deep learning skills.",
    job_skills_str="['Python', 'Machine Learning', 'Deep Learning', 'PyTorch']"
)
print(res)
```
