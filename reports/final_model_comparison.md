# CareerIQ — Final Model Comparison & Audit Verification Report

**Date:** October 11, 2026  
**Platform:** CareerIQ AI Platform  
**System Environment:** Windows AMD64 | Python 3.14.7 | PyTorch 2.14.1+cpu  
**Backup Location:** `C:\CareerMind_AI\backups\models_backup\`  

---

## 1. Comparative Performance Table

| Component | Old Reported Metrics | Actual Measured Metrics | Evaluation Split | Status |
|---|---|---|---|---|
| **Resume NER** | Token Acc: 93.50% | Token Acc: **93.50%**<br>Micro F1: **47.93%**<br>Precision: **46.02%**<br>Recall: **50.00%**<br>Macro F1: **39.00%** | Untouched Test Set (22 resumes, 10%) | **Verified & Clarified**<br>*(Token accuracy confirmed at 93.50%; entity-level F1 is 47.93% due to ~94% non-entity 'O' tokens and class imbalance).* |
| **Resume Classification** | Ensemble Acc: 88.35%<br>Ensemble F1: 0.876 | Ensemble Acc: **88.35%**<br>Ensemble F1: **87.64%**<br>DistilBERT Acc: **87.55%**<br>SVM Acc: **70.68%** | Untouched Test Set (249 resumes, 10%) | **Verified & Retained**<br>*(Ensemble justified over standalone models; leakage prevented by fitting TF-IDF strictly on train split).* |
| **Job Matching** | Acc: 82.70%<br>F1: 0.831 | Acc: **82.70%**<br>F1: **83.06%**<br>Precision: **81.38%**<br>Recall: **84.80%** | Untouched Test Set (1,000 pairs, 10%) | **Verified & Retained**<br>*(Raw resume and job datasets split before pairing, preventing pair leakage. XGBoost trained on SBERT features).* |
| **Career Recommendation** | Hit@3: 87.5%<br>Hit@5: 100%<br>MRR: 0.900 | Hit@3: **87.50%**<br>Hit@5: **100.00%**<br>MRR: **0.9000** | Held-Out Queries (8 candidate benchmark profiles) | **Verified & Documented**<br>*(Unsupervised semantic cosine + skill graph retrieval engine accurately mapped to 324 reference roles).* |
| **Job Search** | P@1: 1.00<br>P@3: 1.00 | Mean P@1: **1.00 (100.0%)**<br>Mean P@3: **1.00 (100.0%)** | Held-Out Queries (5 representative domain queries) | **Verified & Documented**<br>*(Hybrid dual retrieval combining TF-IDF lexical index with dense SBERT semantic similarity).* |

---

## 2. In-Depth Analysis of Individual Components

### 2.1 Resume Named Entity Recognition (NER)
- **Investigation of the Discrepancy (93.50% Token Accuracy vs 47.93% Entity F1):**
  - In resume text, entity spans (names, degrees, designations, skills) account for only ~6% of all tokens; the remaining ~94% are generic vocabulary labeled as `"O"` (Outside).
  - A trivial baseline model predicting `"O"` for every single token achieves over 93% token accuracy without identifying a single entity.
  - Evaluation via `seqeval` measures chunk-level entity precision (46.02%) and recall (50.00%), yielding an F1 of 47.93%.
  - High performance was observed on clean entities such as `LOCATION` (F1: 80.0%) and `NAME` (F1: 86.0%), while severe class imbalance degraded rare entities such as `COMPANIES_WORKED_AT` (F1: 5.0%) and `GRADUATION_YEAR` (F1: 0.0%).
- **Verification:** Sliding window chunking (stride 64, max length 512) and label alignment (`-100` for special/subsequent subword tokens) are functioning properly.

### 2.2 Resume Domain Classification
- **Architecture Validation:**
  - TF-IDF + Linear SVM provides a fast baseline (70.68% test accuracy).
  - DistilBERT sequence classifier captures contextual domain semantics (87.55% test accuracy).
  - The soft-voting ensemble (`0.5 * P_svm + 0.5 * P_bert`) achieves peak performance of 88.35% test accuracy and 87.64% weighted F1, justifying the ensemble strategy.
- **Split Quality:** 80/10/10 stratified split across all 24 classes ensures balanced representation of both major and minor classes.

### 2.3 Resume–Job Matching
- **Task & Formulation:** Formulated as a binary classification problem over 8,000 resume-job pairs.
- **Data Leakage Safeguard:** Source resumes and source jobs are split into 80% train, 10% validation, and 10% test partitions *prior* to cross-pairing, guaranteeing that test pairs contain zero resumes or jobs that were exposed during training.
- **Model Role Distinction:** SBERT (`all-MiniLM-L6-v2`) acts as a frozen semantic feature extractor; XGBoost is the learned classifier trained on cosine similarities, skill overlaps, and embedding difference/product interaction features.

### 2.4 Career Recommendation
- **Nature of System:** Clarified and documented as an unsupervised ranking and knowledge retrieval engine rather than a supervised neural network.
- **Evaluation Validity:** Evaluated against 8 distinct ground-truth candidate resume profiles covering various domains (Engineering, Data Science, Culinary, Trade, Healthcare). Demonstrates 87.50% Hit@3, 100.00% Hit@5, and 0.9000 MRR.

### 2.5 Semantic Job Search
- **Nature of System:** Information retrieval pipeline indexing 521 job postings.
- **Hybrid Retrieval Weights:** Lexical TF-IDF weight (0.4) combined with dense SBERT semantic similarity (0.6).
- **Evaluation Validity:** Evaluated on benchmark queries, achieving 100% P@1 and P@3 across relevant job title matches.

---

## 3. Directory Layout Compliance (Phase 3 & Phase 7)

All five models now adhere strictly to the standardized directory architecture:

```
C:\CareerMind_AI\models\<model_name>\
├── dataset_info\
│   ├── dataset_summary.json
│   ├── dataset_schema.json
│   ├── label_distribution.json
│   ├── data_quality_report.json
│   ├── split_summary.json
│   └── split_config.json
├── preprocessing\
├── training\
├── testing\
├── saved_model\
├── evaluation\
├── inference.py
└── README.md
```

All inference modules have been verified and can be imported and executed independently.
