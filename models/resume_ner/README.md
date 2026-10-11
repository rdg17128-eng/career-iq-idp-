# Resume Named Entity Recognition (NER)

## Overview
This module fine-tunes a Transformer token classifier (`roberta-base`) to identify and extract entity spans from raw unstructured resume documents.

## Dataset Information
- **Original Dataset Location:** `C:\CareerMind_AI\datasets\resume_ner_dataset\train\train_data.json`
- **Total Resumes:** 220 documents
- **Entity Classes (11):** `COLLEGE_NAME`, `COMPANIES_WORKED_AT`, `DEGREE`, `DESIGNATION`, `EMAIL_ADDRESS`, `GRADUATION_YEAR`, `LOCATION`, `NAME`, `SKILLS`, `UNKNOWN`, `YEARS_OF_EXPERIENCE`
- **Tagging Scheme:** BIO format (`B-*`, `I-*`, `O`), resulting in 23 target classes.

## Preprocessing & Data Splitting
- **Script:** `preprocessing/preprocess_ner.py`
- **Tokenization:** Sliding window chunking with max sequence length 512 and stride 64.
- **Label Alignment:** First subword token receives the entity tag; subsequent subwords and special tokens are labeled with `-100` (ignored during backprop and loss calculation).
- **Split Scheme:** Document-level split (80% Train, 10% Validation, 10% Test).
  - Train: 176 resumes
  - Validation: 22 resumes
  - Test: 22 resumes

## Training & Evaluation
- **Training Script:** `training/train_ner.py`
- **Evaluation Script:** `evaluation/evaluate_ner.py`
- **Testing Script:** `testing/test_ner.py`
- **Hardware Mode:** CPU Fallback / GPU compatible

### Performance Metrics (Untouched Test Split)
- **Token Accuracy:** 93.50%
- **Entity Micro Precision:** 46.02%
- **Entity Micro Recall:** 50.00%
- **Entity Micro F1:** 47.93%
- **Macro F1:** 39.00%

> **Insight:** Token accuracy is ~93.50% because background non-entity tokens (`O`) represent ~94% of all resume tokens. Entity chunk F1 (47.93%) is the true test of candidate information extraction.

## Saved Model Artifacts
Stored in `saved_model/` and root directory:
- `model.safetensors` (RoBERTa weights)
- `config.json`
- `tokenizer.json` & `tokenizer_config.json`
- `label_map.json`

## Inference Usage
```python
from models.resume_ner.inference import ResumeNERExtractor

extractor = ResumeNERExtractor()
entities = extractor.extract_entities("Alice Clark - Software Engineer at Google with Python and Docker skills.")
print(entities)
```
