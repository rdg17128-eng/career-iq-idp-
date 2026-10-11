# Semantic & Hybrid Job Description Search Engine

## Overview
A dual-retrieval search engine combining sparse lexical indexing (TF-IDF) with dense semantic vector representations (Sentence-BERT) to search unstructured job postings with high precision.

## Pipeline Nature
This component is an **information retrieval and indexing pipeline**. Pretrained Sentence-BERT embeddings and a fitted TF-IDF sparse matrix are used without supervised neural training.

## Dataset Information
- **Original Dataset Location:** `C:\CareerMind_AI\datasets\job_description_dataset\data.csv`
- **Total Indexed Documents:** 521 job postings.
- **Fields:** `Job Title`, `Description`.

## Search Architecture
- **Lexical Index:** `TfidfVectorizer(max_features=10000, stop_words='english', ngram_range=(1, 2))`
- **Semantic Index:** Dense embeddings generated using `all-MiniLM-L6-v2`.
- **Hybrid Scoring Formula:**
  $$\text{Score} = w_{\text{tfidf}} \cdot S_{\text{lexical}} + w_{\text{sbert}} \cdot S_{\text{semantic}}$$
  where default $w_{\text{tfidf}} = 0.4$ and $w_{\text{sbert}} = 0.6$.

## Evaluation
- **Evaluation Script:** `evaluation/evaluate_search.py`
- **Benchmark:** Multi-domain search query benchmark (`Data Analyst`, `Business Analyst`, `Marketing Data Analyst`, `Business Intelligence Analyst`, `Supply Chain Data Analyst`).

### Metrics
- **Mean Precision @ 1:** **1.00 (100.0%)**
- **Mean Precision @ 3:** **1.00 (100.0%)**

## Saved Artifacts
Stored in `saved_model/` and root directory:
- `data.csv`
- `tfidf_vectorizer.joblib`
- `tfidf_index.joblib`
- `sbert_index.joblib`

## Inference Usage
```python
from models.job_search.inference import JobSearchEngine

searcher = JobSearchEngine()
results = searcher.search(query="Data Analyst Python SQL", top_k=5)
for r in results:
    print(r['rank'], r['job_title'], r['hybrid_score'])
```
