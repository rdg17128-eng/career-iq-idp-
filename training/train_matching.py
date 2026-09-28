import os
import pandas as pd
import json
import joblib
import ast
import torch
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from sentence_transformers import SentenceTransformer
from xgboost import XGBClassifier

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.replace("\r", " ").replace("\n", " ")
    return " ".join(text.split())

def generate_pairs(resumes_df, jobs_df, max_pairs=6000, random_seed=42):
    np.random.seed(random_seed)
    
    # Categories that exist in both datasets
    shared_categories = ['HR', 'INFORMATION-TECHNOLOGY', 'SALES', 'FINANCE', 'BUSINESS-DEVELOPMENT']
    
    # Filter both dataframes to shared categories
    resumes_df = resumes_df[resumes_df['Category'].isin(shared_categories)].copy()
    jobs_df = jobs_df[jobs_df['category'].isin(shared_categories)].copy()
    
    pos_pairs = []
    neg_pairs = []
    
    # Generate positive pairs (Category Match)
    for category in shared_categories:
        cat_resumes = resumes_df[resumes_df['Category'] == category]
        cat_jobs = jobs_df[jobs_df['category'] == category]
        
        for _, resume in cat_resumes.iterrows():
            for _, job in cat_jobs.iterrows():
                pos_pairs.append({
                    'resume_text': resume['Resume_str'],
                    'job_description': job['job_description'],
                    'job_skills': job['job_skill_set'],
                    'resume_category': resume['Category'],
                    'job_category': job['category'],
                    'label': 1
                })
                
    # Generate negative pairs (Category Mismatch)
    for category in shared_categories:
        cat_resumes = resumes_df[resumes_df['Category'] == category]
        other_jobs = jobs_df[jobs_df['category'] != category]
        
        # Sample jobs to avoid explosive growth
        if len(other_jobs) > 100:
            other_jobs = other_jobs.sample(100, random_state=random_seed)
            
        for _, resume in cat_resumes.iterrows():
            for _, job in other_jobs.iterrows():
                neg_pairs.append({
                    'resume_text': resume['Resume_str'],
                    'job_description': job['job_description'],
                    'job_skills': job['job_skill_set'],
                    'resume_category': resume['Category'],
                    'job_category': job['category'],
                    'label': 0
                })
                
    # Balance positive and negative pairs
    num_pos = len(pos_pairs)
    num_neg = len(neg_pairs)
    
    target_pos = min(num_pos, max_pairs // 2)
    target_neg = min(num_neg, max_pairs // 2)
    
    print(f"Total possible positive pairs: {num_pos}, negative: {num_neg}")
    print(f"Sampling target positive: {target_pos}, negative: {target_neg}")
    
    # Shuffle lists
    np.random.shuffle(pos_pairs)
    np.random.shuffle(neg_pairs)
    
    sampled_pos = pos_pairs[:target_pos]
    sampled_neg = neg_pairs[:target_neg]
    
    all_pairs = sampled_pos + sampled_neg
    np.random.shuffle(all_pairs)
    
    return pd.DataFrame(all_pairs)

def extract_features(pairs_df, sbert_model):
    print("Computing Sentence-BERT embeddings...")
    # Embed text on GPU
    resume_embeddings = sbert_model.encode(
        pairs_df['resume_text'].tolist(),
        show_progress_bar=True,
        convert_to_numpy=True
    )
    job_embeddings = sbert_model.encode(
        pairs_df['job_description'].tolist(),
        show_progress_bar=True,
        convert_to_numpy=True
    )
    
    print("Computing similarity and skill overlap features...")
    X_features = []
    
    for idx, row in pairs_df.iterrows():
        E_res = resume_embeddings[idx]
        E_job = job_embeddings[idx]
        
        # 1. Cosine similarity
        cos_sim = np.dot(E_res, E_job) / (np.linalg.norm(E_res) * np.linalg.norm(E_job) + 1e-8)
        
        # 2. Skill overlap
        job_skills_str = row['job_skills']
        try:
            job_skills = set([s.lower() for s in ast.literal_eval(job_skills_str)])
        except Exception:
            job_skills = set()
            
        resume_text_lower = str(row['resume_text']).lower()
        matched_skills = [s for s in job_skills if s in resume_text_lower]
        skill_overlap = len(matched_skills) / len(job_skills) if len(job_skills) > 0 else 0.0
        
        # 3. Interactive embedding features
        diff = np.abs(E_res - E_job)
        mult = E_res * E_job
        
        # Combine
        feat_vector = [cos_sim, skill_overlap] + diff.tolist() + mult.tolist()
        X_features.append(feat_vector)
        
    return np.array(X_features), np.array(pairs_df['label'].tolist())

def main():
    print("Initializing Resume-Job Matching training...")
    
    # Paths
    jobs_csv = r"c:\CareerMind_AI\datasets\job_matching_dataset\all_job_post.csv"
    resumes_csv = r"c:\CareerMind_AI\datasets\resume_classification_dataset\Resume\Resume.csv"
    model_dir = r"c:\CareerMind_AI\models\job_matching"
    
    if not (os.path.exists(jobs_csv) and os.path.exists(resumes_csv)):
        print("Error: Missing job post dataset or resume dataset.")
        return
        
    os.makedirs(os.path.join(model_dir, "xgboost"), exist_ok=True)
    os.makedirs(os.path.join(model_dir, "preprocessing"), exist_ok=True)
    
    # Load raw datasets
    df_resumes = pd.read_csv(resumes_csv)
    df_jobs = pd.read_csv(jobs_csv)
    
    # Light clean
    df_resumes['Resume_str'] = df_resumes['Resume_str'].apply(clean_text)
    df_jobs['job_description'] = df_jobs['job_description'].apply(clean_text)
    
    # Data Leakage Prevention: Split source dataframes before pairing!
    print("Splitting source datasets (Train 80%, Val 10%, Test 10%)...")
    res_train, res_temp = train_test_split(df_resumes, test_size=0.20, random_state=42, stratify=df_resumes['Category'])
    res_val, res_test = train_test_split(res_temp, test_size=0.50, random_state=42, stratify=res_temp['Category'])
    
    job_train, job_temp = train_test_split(df_jobs, test_size=0.20, random_state=42, stratify=df_jobs['category'])
    job_val, job_test = train_test_split(job_temp, test_size=0.50, random_state=42, stratify=job_temp['category'])
    
    # Generate paired dataframes
    print("\n--- Generating Train pairs ---")
    train_pairs = generate_pairs(res_train, job_train, max_pairs=6000)
    
    print("\n--- Generating Validation pairs ---")
    val_pairs = generate_pairs(res_val, job_val, max_pairs=1000)
    
    print("\n--- Generating Test pairs ---")
    test_pairs = generate_pairs(res_test, job_test, max_pairs=1000)
    
    # Load Sentence-BERT on GPU
    print("\nLoading Sentence-BERT model (all-MiniLM-L6-v2)...")
    sbert = SentenceTransformer('all-MiniLM-L6-v2')
    if torch.cuda.is_available():
        sbert = sbert.to('cuda')
        print("SBERT running on: GPU")
    else:
        print("SBERT running on: CPU")
        
    # Feature extraction
    print("\nExtracting features for Training split...")
    X_train, y_train = extract_features(train_pairs, sbert)
    
    print("\nExtracting features for Validation split...")
    X_val, y_val = extract_features(val_pairs, sbert)
    
    print("\nExtracting features for Test split...")
    X_test, y_test = extract_features(test_pairs, sbert)
    
    # Save test features to disk for evaluation script to avoid re-embedding
    test_split_path = os.path.join(model_dir, "preprocessing", "test_split.joblib")
    print(f"Saving test split features to {test_split_path}...")
    joblib.dump({"X_test": X_test, "y_test": y_test, "test_pairs": test_pairs}, test_split_path)
    
    # Train XGBoost Classifier
    print("\n--- Training XGBoost Classifier ---")
    model = XGBClassifier(
        n_estimators=150,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
        tree_method='hist',
        eval_metric='logloss',
        early_stopping_rounds=15
    )
    
    print("Fitting XGBClassifier...")
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=True
    )
    
    # Evaluate on Train and Val
    train_preds = model.predict(X_train)
    val_preds = model.predict(X_val)
    
    train_acc = accuracy_score(y_train, train_preds)
    val_acc = accuracy_score(y_val, val_preds)
    
    train_f1 = f1_score(y_train, train_preds, average='weighted')
    val_f1 = f1_score(y_val, val_preds, average='weighted')
    
    print(f"\nTraining Results:")
    print(f"  Train Accuracy: {train_acc*100:.2f}% | F1: {train_f1*100:.2f}%")
    print(f"  Val Accuracy:   {val_acc*100:.2f}% | F1: {val_f1*100:.2f}%")
    
    # Save XGBoost model
    xgb_path = os.path.join(model_dir, "xgboost", "matching_xgboost.json")
    print(f"Saving XGBoost model to {xgb_path}...")
    model.save_model(xgb_path)
    
    # Save training metrics
    metrics_summary = {
        "train_accuracy": train_acc,
        "train_f1": train_f1,
        "val_accuracy": val_acc,
        "val_f1": val_f1
    }
    with open(os.path.join(model_dir, "training_metrics.json"), "w") as f:
        json.dump(metrics_summary, f, indent=2)
        
    print("Resume-Job Matching model trained and saved successfully!")

if __name__ == "__main__":
    main()
