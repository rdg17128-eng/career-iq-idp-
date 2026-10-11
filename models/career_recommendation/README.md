# Career Trajectory & Role Recommender

## Overview
An intelligent recommendation and ranking system that evaluates candidate resumes against 324 standardized industry roles, computes semantic affinity using Sentence-BERT embeddings, detects missing required skills, and generates career next steps.

## Pipeline Nature
This component is an **unsupervised semantic ranking & skill-graph retrieval engine** rather than a supervised neural classifier. It utilizes dense cosine similarity and rule-based skill overlap metrics to rank roles.

## Dataset Information
- **Original Dataset Location:** `C:\CareerMind_AI\datasets\career_role_skill_dataset\`
  - `job_roles.csv`: 324 occupational reference profiles with required skills and salary data.
  - `skills_list.csv`: 120 standardized taxonomy skills.
  - `test_resumes.json`: 8 held-out ground-truth evaluation profiles.
  - `training_data.csv`: 10,000 synthetic resume records.

## Preprocessing & Ranking Logic
- **Pre-computed Embeddings:** Role profiles (Title, Category, Required Skills) are embedded using `all-MiniLM-L6-v2`.
- **Candidate Skill Matching:** Candidate resume text is analyzed for skill occurrences with word boundary detection.
- **Scoring:** Composite score combining dense cosine similarity and candidate skill match percentage.

## Evaluation
- **Evaluation Script:** `evaluation/evaluate_recommender.py`
- **Benchmark:** 8 diverse candidate profiles in `test_resumes.json`.

### Ranking Metrics
- **Hit Rate @ 3:** **87.50%**
- **Hit Rate @ 5:** **100.00%**
- **Mean Reciprocal Rank (MRR):** **0.9000**

## Saved Artifacts
Stored in `saved_model/` and root directory:
- `job_roles.csv` (Reference profile database)

## Inference Usage
```python
from models.career_recommendation.inference import CareerRoleRecommender

recommender = CareerRoleRecommender()
recommendations = recommender.recommend(
    resume_text="Full stack web developer experienced with React, Node.js, JavaScript, and MongoDB.",
    top_k=5
)
for rec in recommendations:
    print(rec['role'], rec['match_score'], rec['missing_skills'])
```
