import os
import json
import numpy as np
from models.career_recommendation.inference import CareerRoleRecommender

def clean_title(title):
    return str(title).lower().strip().replace("-", " ").replace("_", " ")

def main():
    print("Initializing Career Role/Skill Recommendation evaluation...")
    
    test_json_path = r"c:\career iq\datasets\career_role_skill_dataset\test_resumes.json"
    model_dir = r"c:\career iq\models\career_recommendation"
    
    if not os.path.exists(test_json_path):
        print(f"Error: Test resumes not found at {test_json_path}")
        return
        
    # Load test cases
    with open(test_json_path, 'r', encoding='utf-8') as f:
        test_cases = json.load(f)
    print(f"Loaded {len(test_cases)} test cases for evaluation.")
    
    # Initialize recommender
    recommender = CareerRoleRecommender(model_dir=model_dir)
    
    hits_at_3 = 0
    hits_at_5 = 0
    reciprocal_ranks = []
    
    detailed_results = []
    
    for idx, case in enumerate(test_cases):
        name = case.get('name', f"Candidate {idx+1}")
        resume_text = case.get('resume_text', '')
        expected_roles = [clean_title(r) for r in case.get('expected_roles', [])]
        
        # Run recommender (get top 10 recommendations)
        recommendations = recommender.recommend(resume_text, top_k=10)
        recommended_titles = [clean_title(r['role']) for r in recommendations]
        
        # Calculate Rank metrics
        hit_3 = 0
        hit_5 = 0
        rr = 0.0
        
        for rank, rec_title in enumerate(recommended_titles):
            # Check if recommended title matches any expected roles
            if any(rec_title == exp_role or exp_role in rec_title or rec_title in exp_role for exp_role in expected_roles):
                # We found a hit!
                if rank < 3:
                    hit_3 = 1
                if rank < 5:
                    hit_5 = 1
                rr = 1.0 / (rank + 1)
                break
                
        hits_at_3 += hit_3
        hits_at_5 += hit_5
        reciprocal_ranks.append(rr)
        
        # Keep detailed info
        detailed_results.append({
            "name": name,
            "expected_roles": case.get('expected_roles', []),
            "top_3_recommendations": [r['role'] for r in recommendations[:3]],
            "hit_at_3": hit_3,
            "hit_at_5": hit_5,
            "reciprocal_rank": rr
        })
        
    # Aggregate metrics
    num_cases = len(test_cases)
    hit_rate_at_3 = hits_at_3 / num_cases if num_cases > 0 else 0.0
    hit_rate_at_5 = hits_at_5 / num_cases if num_cases > 0 else 0.0
    mrr = np.mean(reciprocal_ranks) if len(reciprocal_ranks) > 0 else 0.0
    
    print("\nEvaluation Results on Test Resumes:")
    print(f"  Hit Rate @ 3: {hit_rate_at_3*100:.2f}%")
    print(f"  Hit Rate @ 5: {hit_rate_at_5*100:.2f}%")
    print(f"  MRR:          {mrr:.4f}")
    
    # Save metrics to metrics.json
    metrics_report = {
        "hit_rate_at_3": hit_rate_at_3,
        "hit_rate_at_5": hit_rate_at_5,
        "mean_reciprocal_rank": mrr,
        "detailed_results": detailed_results
    }
    
    metrics_path = os.path.join(model_dir, "metrics.json")
    with open(metrics_path, 'w') as f:
        json.dump(metrics_report, f, indent=2)
        
    print(f"\nRecommendation evaluation metrics saved to {metrics_path}")

if __name__ == "__main__":
    main()
