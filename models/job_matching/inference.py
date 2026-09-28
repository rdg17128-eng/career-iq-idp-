import os
import ast
import torch
import numpy as np
from sentence_transformers import SentenceTransformer
from xgboost import XGBClassifier

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.replace("\r", " ").replace("\n", " ")
    return " ".join(text.split())

class ResumeJobMatcher:
    def __init__(self, model_dir=None):
        if model_dir is None:
            model_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_dir = model_dir
        
        # Load Sentence-BERT
        print("[Matcher Inference] Loading Sentence-BERT model (all-MiniLM-L6-v2)...")
        self.sbert = SentenceTransformer('all-MiniLM-L6-v2')
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.sbert = self.sbert.to(self.device)
        print(f"  - SBERT running on: {self.device}")
        
        # Load XGBoost model
        xgb_path = os.path.join(model_dir, "xgboost", "matching_xgboost.json")
        print(f"  - Loading XGBoost model from {xgb_path}")
        self.model = XGBClassifier()
        self.model.load_model(xgb_path)
        print("Matching system initialized successfully!")

    def predict(self, resume_text, job_description, job_skills_str="[]"):
        # Clean inputs
        res_clean = clean_text(resume_text)
        job_clean = clean_text(job_description)
        
        # Embed texts
        E_res = self.sbert.encode(res_clean, convert_to_numpy=True)
        E_job = self.sbert.encode(job_clean, convert_to_numpy=True)
        
        # Compute Cosine Similarity
        cos_sim = np.dot(E_res, E_job) / (np.linalg.norm(E_res) * np.linalg.norm(E_job) + 1e-8)
        
        # Compute Skill Overlap ratio
        try:
            if isinstance(job_skills_str, str):
                job_skills = set([s.lower() for s in ast.literal_eval(job_skills_str)])
            elif isinstance(job_skills_str, (list, set)):
                job_skills = set([s.lower() for s in job_skills_str])
            else:
                job_skills = set()
        except Exception:
            job_skills = set()
            
        res_lower = res_clean.lower()
        matched_skills = [s for s in job_skills if s in res_lower]
        skill_overlap = len(matched_skills) / len(job_skills) if len(job_skills) > 0 else 0.0
        
        # Compute interactive features
        diff = np.abs(E_res - E_job)
        mult = E_res * E_job
        
        # Combine features
        feat_vector = [cos_sim, skill_overlap] + diff.tolist() + mult.tolist()
        X_input = np.array([feat_vector])
        
        # Predict
        prob = float(self.model.predict_proba(X_input)[0, 1])
        matched = int(self.model.predict(X_input)[0])
        
        return matched, prob, list(matched_skills)

def main():
    matcher = ResumeJobMatcher()
    
    # Test cases
    resume = (
        "Alice Smith - Senior Software Engineer. Technical Skills: Python, Java, Docker, Kubernetes, SQL. "
        "Experience: 5 years building scalable microservices and backend APIs in cloud environments."
    )
    
    job_desc = (
        "We are looking for a Senior Backend Developer to join our engineering team. "
        "You will design and build scalable services, microservices, and databases. "
        "Requirements: Experience with Python or Java. Familiarity with cloud technologies (Docker, Kubernetes) is a plus."
    )
    
    required_skills = "['Python', 'Java', 'Docker', 'Kubernetes', 'Microservices', 'SQL', 'Git']"
    
    print("\nRunning matching test...")
    print("=" * 60)
    matched, score, matched_skills = matcher.predict(resume, job_desc, required_skills)
    print(f"Match Prediction: {'MATCHED' if matched == 1 else 'MISMATCHED'}")
    print(f"Match Probability: {score * 100:.2f}%")
    print(f"Matched Skills: {matched_skills}")
    print("=" * 60)

if __name__ == "__main__":
    main()
