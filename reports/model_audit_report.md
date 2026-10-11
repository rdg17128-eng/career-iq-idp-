# Model Audit Report — CareerIQ AI Platform

**Generated Date:** October 11, 2026  
**Auditor:** Antigravity AI Engine  
**Project Root:** `C:\CareerMind_AI\` (Junction linked to `C:\career iq\`)  
**Hardware / OS:** Windows AMD64 | Python 3.14.7 | PyTorch 2.14.1+cpu (CPU Execution Mode)

---

## Executive Summary & High-Level Audit Findings

An exhaustive audit of all five Machine Learning and NLP components in **CareerIQ** was performed across dataset files, data schemas, missing/duplicate values, split logic, preprocessing pipelines, training implementations, evaluation metrics, and model directories.

| # | Component / Engine | Dataset Name & Format | Usable Records | Architecture | Current Key Metric | Status & Main Issue Identified |
|---|---|---|---|---|---|---|
| 1 | **Resume NER** | `resume_ner_dataset` (JSON) | 220 resumes | RoBERTa Token Classifier (`roberta-base`) | **93.50%** Token Acc, **47.93%** Entity F1 | **Severe Class Imbalance & Annotation Sparsity:** 93.5% token accuracy is dominated by background `"O"` tokens (~94%), while entity chunk F1 is 47.93%. Needs entity-level metrics reporting, token-to-subword alignment preservation, and per-document splitting. |
| 2 | **Resume Classification** | `resume_classification_dataset` (CSV) | 2,484 resumes (24 classes) | TF-IDF + Linear SVM & DistilBERT Ensemble | **88.35%** Acc (Ensemble), **85.95%** F1 (Transformer), **70.16%** Acc (SVM) | **Ensemble Justification & Leakage:** Preprocessing cleans text appropriately. Stratified 80/10/10 split is used. TF-IDF fitted on train split. Transformer outclasses SVM significantly; soft-voting ensemble marginally improves test accuracy to 88.35%. |
| 3 | **Resume–Job Matching** | `job_matching_dataset` + `Resume.csv` (CSV) | 1,167 jobs & 2,484 resumes (8,000 generated pairs) | Sentence-BERT (`all-MiniLM-L6-v2`) + XGBoost Classifier | **82.70%** Test Acc, **83.06%** F1 | **Binary Classification Formulation:** Evaluated on balanced positive/negative pairs generated across 5 shared industrial categories. Cross-split pair leakage was prevented by splitting raw resumes and jobs prior to Cartesian pairing. Pretrained SBERT embeddings are extracted; XGBoost is fitted strictly on train pairs. |
| 4 | **Career Recommendation** | `career_role_skill_dataset` (CSV + JSON) | 324 job roles, 120 skills, 8 test profiles | Dense SBERT Embedding + Skill-Overlap Graph Ranker | **87.5%** Hit@3, **100.0%** Hit@5, **0.900** MRR | **Recommendation & Retrieval Pipeline:** This is an unsupervised/ranking pipeline, not a supervised neural classifier. Employs 324 reference roles. Tested against 8 curated candidate benchmark profiles. Reference data was improperly stored only in the model folder without structured metadata schemas. |
| 5 | **Semantic Job Search** | `job_description_dataset` (CSV) | 521 job postings | Hybrid TF-IDF Lexical + SBERT Semantic Retrieval Engine | **1.00** P@1, **1.00** P@3 | **Hybrid Retrieval System:** Combines sparse TF-IDF (weight 0.4) and dense SBERT embeddings (weight 0.6). Tested against domain benchmark search queries. The index stores 521 searchable job postings. Must be documented as an indexing pipeline rather than supervised model training. |

---

## Detailed Model Audits

### 1. Resume Named Entity Recognition (NER)

- **Dataset Name & Location:** `resume_ner_dataset`, located at `C:\CareerMind_AI\datasets\resume_ner_dataset\`
  - Primary file: `train\train_data.json` (220 annotated resumes in JSON format)
  - Raw test files: `test\` contains `Alice Clark CV.pdf/docx/txt`, `Smith Resume.pdf/docx` (unannotated test resumes for inference testing)
- **Original Dataset Size:** 220 document records.
- **Number of Usable Records:** 220 documents.
- **Dataset Columns / Schema:**
  - `text`: Raw text string of the resume.
  - `entities`: List of entity spans formatted as `[start_char, end_char, label]`.
  - Unique Target Entity Labels (11): `COLLEGE_NAME`, `COMPANIES_WORKED_AT`, `DEGREE`, `DESIGNATION`, `EMAIL_ADDRESS`, `GRADUATION_YEAR`, `LOCATION`, `NAME`, `SKILLS`, `UNKNOWN`, `YEARS_OF_EXPERIENCE`.
  - BIO Tag Schema: 23 classes (`O` + 11 `B-*` tags + 11 `I-*` tags).
- **Missing-Value Statistics:** 0 null texts; all 220 records contain entity lists.
- **Duplicate-Record Statistics:** 0 exact duplicate resumes found in the JSON dataset.
- **Existing Preprocessing Steps:**
  - Sliding window tokenization with stride 64 tokens, max length 512 using RoBERTa tokenizer.
  - Subword-to-label alignment: first subword of an entity token receives `B-<LABEL>` or `I-<LABEL>`, subsequent subwords and special tokens receive label `-100` (ignored in loss computation).
  - Train/Val/Test document-level split (176 train / 22 val / 22 test, 80/10/10).
- **Missing or Incorrect Preprocessing Steps:**
  - The evaluation script previously emphasized token accuracy over entity chunk F1.
  - High token accuracy (~93.5%) was masking weak entity recall on rare classes like `COMPANIES_WORKED_AT` (F1: 0.05) and `GRADUATION_YEAR` (F1: 0.00).
- **Existing Training and Testing Procedures:**
  - Fine-tuned `roberta-base` for 5 epochs with Hugging Face `Trainer`.
  - Evaluated using `seqeval` computing precision, recall, and F1 on non-ignored tokens (`label != -100`).
- **Existing Train/Validation/Test Sizes:**
  - Train: 176 resumes (80%)
  - Validation: 22 resumes (10%)
  - Test: 22 resumes (10%)
- **Current Model Architecture:**
  - Base Model: `roberta-base` (`AutoModelForTokenClassification`)
  - Sequence Length: 512 tokens with sliding window stride of 64
  - Saved Weights: `model.safetensors` (496 MB), `tokenizer.json`, `config.json`
- **Current Evaluation Metrics:**
  - Token-Level Accuracy: **93.50%**
  - Entity-Level Micro Precision: **46.02%**
  - Entity-Level Micro Recall: **50.00%**
  - Entity-Level Micro F1: **47.93%**
  - Macro F1: **39.00%**
- **Problems Found:**
  - Disconnect between 93.50% accuracy and 47.93% F1: In token classification, over 93% of all tokens in a resume are non-entities (`O`). A baseline model predicting `O` for every token easily scores >93% token accuracy.
  - Severe class imbalance: `SKILLS` has 66 instances in test split, whereas `UNKNOWN` has 1, `YEARS_OF_EXPERIENCE` has 3, and `COMPANIES_WORKED_AT` has 20.
  - The model directory lacked standardized subfolder organization (`dataset_info`, `preprocessing`, `training`, `testing`, `saved_model`, `evaluation`).
- **Required Corrective Actions:**
  - Organize into standard folder hierarchy.
  - Save `dataset_summary.json`, `dataset_schema.json`, `label_distribution.json`, and `data_quality_report.json` under `dataset_info`.
  - Keep `saved_model` equipped with all tokenizer and weights artifacts for standalone inference.

---

### 2. Resume Domain Classification

- **Dataset Name & Location:** `resume_classification_dataset`, located at `C:\CareerMind_AI\datasets\resume_classification_dataset\`
  - Primary file: `Resume\Resume.csv` (56.3 MB)
- **Original Dataset Size:** 2,484 rows.
- **Number of Usable Records:** 2,484 rows.
- **Dataset Columns / Schema:**
  - `ID`: Unique integer identifier.
  - `Resume_str`: Full raw text string of the resume.
  - `Resume_html`: HTML markup representation of the resume.
  - `Category`: Target domain label (24 unique classes: `ACCOUNTANT`, `ADVOCATE`, `AGRICULTURE`, `APPAREL`, `ARTS`, `AUTOMOBILE`, `AVIATION`, `BANKING`, `BPO`, `BUSINESS-DEVELOPMENT`, `CHEF`, `CONSTRUCTION`, `CONSULTANT`, `DESIGNER`, `DIGITAL-MEDIA`, `ENGINEERING`, `FINANCE`, `FITNESS`, `HEALTHCARE`, `HR`, `INFORMATION-TECHNOLOGY`, `PUBLIC-RELATIONS`, `SALES`, `TEACHER`).
- **Missing-Value Statistics:** 0 nulls across all 4 columns.
- **Duplicate-Record Statistics:** 2 duplicate texts on `Resume_str` across different IDs.
- **Existing Preprocessing Steps:**
  - Text normalization: whitespace collapse, newline removal.
  - Stratified 80/10/10 split on Category label (Train: 1,986, Val: 248, Test: 249).
  - TF-IDF fitted strictly on training data (`max_features=10000`, n-gram range 1-2).
  - DistilBERT tokenization with truncation to 512 tokens.
- **Existing Training and Testing Procedures:**
  - Model A: LinearSVC trained on training TF-IDF vectors.
  - Model B: DistilBERT sequence classifier fine-tuned on training split for 5 epochs.
  - Model C: Hybrid soft-voting ensemble combining SVM decision function probabilities (via softmax) and DistilBERT output probabilities (50% / 50% weighting).
- **Existing Train/Validation/Test Sizes:**
  - Train: 1,986 samples (80.0%)
  - Validation: 248 samples (10.0%)
  - Test: 249 samples (10.0%)
- **Current Model Architecture:**
  - TF-IDF + LinearSVC (`classification_pipeline.joblib`)
  - DistilBERT Sequence Classifier (`distilbert-base-uncased`, 268 MB `model.safetensors`)
  - Soft-voting ensemble module (`ensemble_config.json`)
- **Current Evaluation Metrics (Test Set):**
  - **TF-IDF + Linear SVM:** Accuracy: **70.68%**, Weighted F1: **69.80%**
  - **DistilBERT Transformer:** Accuracy: **87.55%**, Weighted F1: **87.21%**
  - **Hybrid Ensemble:** Accuracy: **88.35%**, Weighted F1: **87.64%**
- **Problems Found:**
  - Disorganized directory layout: splits and models resided alongside root files.
  - Missing standalone evaluation scripts and metadata files.
- **Required Corrective Actions:**
  - Structure into `dataset_info`, `preprocessing`, `training`, `testing`, `saved_model`, and `evaluation`.
  - Save `dataset_summary.json`, `dataset_schema.json`, `label_distribution.json`, and `data_quality_report.json`.

---

### 3. Resume–Job Matching

- **Dataset Name & Location:** `job_matching_dataset`, located at `C:\CareerMind_AI\datasets\job_matching_dataset\`
  - Primary file: `all_job_post.csv` (4.9 MB, 1,167 job postings)
  - Paired with: `Resume.csv` (from `resume_classification_dataset`)
- **Original Dataset Size:** 1,167 job postings; paired into 8,000 resume-job pairs.
- **Number of Usable Records:** 1,167 job postings.
- **Dataset Columns / Schema (`all_job_post.csv`):**
  - `job_id`: Integer identifier.
  - `category`: Job category string.
  - `job_title`: Job position title.
  - `job_description`: Full job description text.
  - `job_skill_set`: Python list string of required skills.
- **Missing-Value Statistics:** 0 nulls across all columns.
- **Duplicate-Record Statistics:** 0 duplicate jobs.
- **Task Formulation:** Binary classification (Match: 1 vs Mismatch: 0).
- **Existing Preprocessing Steps:**
  - Shared categories identified: `HR`, `INFORMATION-TECHNOLOGY`, `SALES`, `FINANCE`, `BUSINESS-DEVELOPMENT`.
  - Source dataframes split *before* pairing (80/10/10 stratified split) to prevent cross-partition pair leakage.
  - SBERT embeddings (`all-MiniLM-L6-v2`) computed for resumes and job descriptions.
  - Feature vector constructed: `[cosine_sim, skill_overlap_ratio] + abs(E_res - E_job) + (E_res * E_job)`.
- **Existing Training and Testing Procedures:**
  - XGBoost Classifier (`max_depth=5`, `learning_rate=0.1`, `n_estimators=150`, `early_stopping_rounds=15`) fitted on training feature matrix.
- **Existing Train/Validation/Test Sizes:**
  - Train pairs: 6,000 (3,000 positive / 3,000 negative)
  - Validation pairs: 1,000 (500 positive / 500 negative)
  - Test pairs: 1,000 (500 positive / 500 negative)
- **Current Model Architecture:**
  - Pretrained Sentence-BERT (`all-MiniLM-L6-v2`) dense text embedder (frozen).
  - XGBoost Gradient Boosted Decision Tree Classifier (`matching_xgboost.json`, 400 KB).
- **Current Evaluation Metrics (Test Set):**
  - Accuracy: **82.70%**
  - Precision: **81.38%**
  - Recall: **84.80%**
  - F1-Score: **83.06%**
  - Confusion Matrix: `[[403, 97], [76, 424]]`
- **Problems Found:**
  - Lack of clear distinction between pretrained SBERT weights and XGBoost model.
  - Directory structure needed organization into modular subfolders.
- **Required Corrective Actions:**
  - Organize into `dataset_info`, `preprocessing`, `training`, `testing`, `saved_model`, and `evaluation`.
  - Document that SBERT is a feature extractor and XGBoost is the learned classifier.

---

### 4. Career Recommendation

- **Dataset Name & Location:** `career_role_skill_dataset`, located at `C:\CareerMind_AI\datasets\career_role_skill_dataset\`
  - Files:
    - `job_roles.csv`: 324 job roles with education, experience, required skills, salary range.
    - `skills_database.json`: 11 skill clusters.
    - `skills_list.csv`: 120 standardized skills with categories.
    - `test_resumes.json`: 8 detailed benchmark candidate profiles with expected target roles.
    - `training_data.csv`: 10,000 synthetic candidate resume records.
    - `career_role_skill_model.joblib`: Pretrained TF-IDF + LogisticRegression pipeline (324 classes).
- **Original Dataset Size:** 324 reference job roles; 120 skills; 8 benchmark test profiles.
- **Number of Usable Records:** 324 job roles; 8 evaluation benchmark profiles.
- **Dataset Columns / Schema (`job_roles.csv`):**
  - `Job Title`, `Category`, `Education Requirement`, `Experience Years`, `Required Skills`, `Salary Range`.
- **Missing-Value Statistics:** 0 nulls in `job_roles.csv`, `skills_list.csv`, or `training_data.csv`.
- **Duplicate-Record Statistics:** 0 duplicates.
- **Task Formulation:** Career recommendation and ranking pipeline based on semantic similarity and skill gap analysis.
- **Existing Preprocessing Steps:**
  - Skill normalization and string cleaning.
  - Pre-computed SBERT embeddings for all 324 job roles.
  - Rule-based keyword skill extraction with boundary detection.
- **Existing Evaluation Procedures:**
  - Evaluated on 8 held-out candidate profiles in `test_resumes.json`.
  - Ranked top-10 recommended roles per candidate against `expected_roles`.
- **Current Evaluation Metrics:**
  - Hit Rate @ 3: **87.50%**
  - Hit Rate @ 5: **100.00%**
  - Mean Reciprocal Rank (MRR): **0.9000**
- **Problems Found:**
  - Directory structure lacked modular breakdown.
  - Job roles database was duplicated in model folder without clear data lineage documentation.
- **Required Corrective Actions:**
  - Reorganize directory structure into required standard layout.
  - Document that the pipeline is an unsupervised ranking and retrieval system rather than a neural classifier.

---

### 5. Semantic Job Search

- **Dataset Name & Location:** `job_description_dataset`, located at `C:\CareerMind_AI\datasets\job_description_dataset\`
  - Primary file: `data.csv` (2.4 MB, 521 job postings)
- **Original Dataset Size:** 521 job postings.
- **Number of Usable Records:** 521 job postings.
- **Dataset Columns / Schema:**
  - `Job Title`: Title string of the job opening.
  - `Description`: Full job description text.
- **Missing-Value Statistics:** 0 nulls across both columns.
- **Duplicate-Record Statistics:** 0 duplicate rows.
- **Task Formulation:** Hybrid information retrieval (sparse lexical TF-IDF + dense semantic SBERT vector search).
- **Existing Preprocessing Steps:**
  - Text normalization: whitespace collapse, newline removal.
  - TF-IDF Vectorizer (`max_features=10000`, `stop_words='english'`, n-gram range 1-2) fitted on the 521 job descriptions.
  - SBERT embeddings (`all-MiniLM-L6-v2`) computed for all 521 job descriptions.
- **Existing Evaluation Procedures:**
  - Evaluated on benchmark search queries (`Data Analyst`, `Business Analyst`, `Marketing Data Analyst`, `Business Intelligence Analyst`, `Supply Chain Data Analyst`).
  - Evaluates Precision@1 and Precision@3 based on title keyword relevance.
- **Current Evaluation Metrics:**
  - Mean Precision @ 1: **1.00 (100.0%)**
  - Mean Precision @ 3: **1.00 (100.0%)**
- **Problems Found:**
  - Lacked modular directory structure.
  - Evaluation was based on small set of 5 queries without full rank correlation metrics.
- **Required Corrective Actions:**
  - Reorganize directory into standard structure.
  - Provide complete dataset summary, schema, and search configuration artifacts.

---

## Action Plan & Verification Matrix

1. **Folder Reorganization:** Establish standard directories (`dataset_info`, `preprocessing`, `training`, `testing`, `saved_model`, `evaluation`, `inference.py`, `README.md`) for all 5 models under `C:\CareerMind_AI\models\`.
2. **Metadata Generation:** Populate `dataset_summary.json`, `dataset_schema.json`, `label_distribution.json`, and `data_quality_report.json` in each model's `dataset_info` directory.
3. **Model Artifact Integrity:** Relocate model checkpoints and index files to `saved_model` subdirectories while maintaining backwards-compatible paths or aliases for inference scripts.
4. **Standalone Testing:** Verify inference and evaluation script execution across all 5 models.
5. **Comparison & Completion Reports:** Generate `final_model_comparison.md` and complete project documentation.
