import os
import shutil
import pandas as pd
import json
import torch
import numpy as np
from sentence_transformers import SentenceTransformer

class CareerRoleRecommender:
    def __init__(self, model_dir=None):
        if model_dir is None:
            model_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_dir = model_dir
        
        # Ensure job_roles.csv is copied locally
        src_csv = r"c:\career iq\datasets\career_role_skill_dataset\job_roles.csv"
        self.db_path = os.path.join(model_dir, "job_roles.csv")
        if os.path.exists(src_csv) and not os.path.exists(self.db_path):
            print(f"[Recommender] Copying job roles database to {self.db_path}...")
            shutil.copy(src_csv, self.db_path)
            
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Job roles database not found at {self.db_path}")
            
        # Load database
        self.df_roles = pd.read_csv(self.db_path)
        print(f"[Recommender] Loaded {len(self.df_roles)} job roles.")
        
        # Load Sentence-BERT
        print("[Recommender] Loading Sentence-BERT model (all-MiniLM-L6-v2)...")
        self.sbert = SentenceTransformer('all-MiniLM-L6-v2')
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.sbert = self.sbert.to(self.device)
        print(f"  - SBERT running on: {self.device}")
        
        # Build set of all skills in database for keyword extraction
        self.all_db_skills = set()
        for idx, row in self.df_roles.iterrows():
            skills_str = row['Required Skills']
            if isinstance(skills_str, str):
                skills = [s.strip().lower() for s in skills_str.split('|')]
                self.all_db_skills.update(skills)
                
        # Pre-compute job role embeddings for fast ranking
        print("[Recommender] Pre-computing job role profile embeddings...")
        role_texts = []
        for idx, row in self.df_roles.iterrows():
            title = row['Job Title']
            cat = row['Category']
            skills = row['Required Skills'].replace('|', ', ') if isinstance(row['Required Skills'], str) else ""
            profile_text = f"Job Title: {title}. Category: {cat}. Required Skills: {skills}."
            role_texts.append(profile_text)
            
        self.role_embeddings = self.sbert.encode(
            role_texts,
            convert_to_numpy=True,
            show_progress_bar=False
        )

    def extract_skills_from_text(self, text):
        text_lower = text.lower()
        extracted = []
        for skill in self.all_db_skills:
            # Word boundary check for short skills to avoid partial matching
            if len(skill) <= 3:
                # Use simple boundaries
                if f" {skill} " in f" {text_lower} " or f"({skill})" in text_lower or f"/{skill}/" in text_lower:
                    extracted.append(skill)
            else:
                if skill in text_lower:
                    extracted.append(skill)
        return set(extracted)

    def recommend(self, resume_text, candidate_skills=None, top_k=5):
        resume_clean = " ".join(resume_text.replace("\r", " ").replace("\n", " ").split())
        
        # 1. Extract/parse candidate skills
        if candidate_skills is None:
            cand_skills = self.extract_skills_from_text(resume_clean)
        else:
            cand_skills = set([s.lower() for s in candidate_skills])
            
        # 2. Embed candidate resume text
        E_cand = self.sbert.encode(resume_clean, convert_to_numpy=True)
        
        # 3. Compute cosine similarity scores for all pre-computed roles
        dots = np.dot(self.role_embeddings, E_cand)
        norms_roles = np.linalg.norm(self.role_embeddings, axis=1)
        norm_cand = np.linalg.norm(E_cand)
        cos_similarities = dots / (norms_roles * norm_cand + 1e-8)
        
        recommendations = []
        
        # 4. Rank each role
        for idx, row in self.df_roles.iterrows():
            title = row['Job Title']
            cat = row['Category']
            required_skills_str = row['Required Skills']
            
            # Parse required skills
            if isinstance(required_skills_str, str):
                req_skills = set([s.strip().lower() for s in required_skills_str.split('|')])
            else:
                req_skills = set()
                
            # Compute skill overlap metrics
            matched_skills = cand_skills.intersection(req_skills)
            missing_skills = req_skills.difference(cand_skills)
            
            skill_overlap_ratio = len(matched_skills) / len(req_skills) if len(req_skills) > 0 else 0.0
            skill_gap_ratio = len(missing_skills) / len(req_skills) if len(req_skills) > 0 else 0.0
            
            # Compute composite match score
            cos_sim = float(cos_similarities[idx])
            # Scale cosine similarity from [-1, 1] to [0, 1]
            cos_sim_scaled = max(0.0, (cos_sim + 1.0) / 2.0)
            
            match_percentage = 0.5 * skill_overlap_ratio + 0.5 * cos_sim_scaled
            
            recommendations.append({
                'role': title,
                'category': cat,
                'match_percentage': float(match_percentage * 100),
                'matched_skills': [s.title() for s in matched_skills],
                'missing_skills': [s.title() for s in missing_skills],
                'skill_gap_percentage': float(skill_gap_ratio * 100),
                'salary_range': row['Salary Range'],
                'experience_required': int(row['Experience Years'])
            })
            
        # Sort by match percentage descending
        recommendations = sorted(recommendations, key=lambda x: x['match_percentage'], reverse=True)
        return recommendations[:top_k]

def main():
    recommender = CareerRoleRecommender()
    
    # Test case
    resume_text = (
        "Alice Smith - Software Engineer. "
        "Education: Bachelor of Science in Computer Science. "
        "Experience: 2 years building backend systems using Java and Spring Boot. "
        "Technical Skills: Python, Java, Spring Boot, Git, SQL, REST APIs, microservices, and Docker."
    )
    
    print("\nRunning recommendation test...")
    print("=" * 60)
    recs = recommender.recommend(resume_text, top_k=3)
    
    for i, rec in enumerate(recs):
        print(f"Recommendation #{i+1}: {rec['role']} ({rec['category']})")
        print(f"  Match Percentage:    {rec['match_percentage']:.2f}%")
        print(f"  Matched Skills:      {rec['matched_skills']}")
        print(f"  Missing Skills:      {rec['missing_skills']}")
        print(f"  Skill Gap:           {rec['skill_gap_percentage']:.2f}%")
        print(f"  Experience Required: {rec['experience_required']} years")
        print(f"  Salary Range:        {rec['salary_range']}")
        print("-" * 60)

if __name__ == "__main__":
    main()
