import os
import json
import numpy as np
from models.job_search.inference import JobSearchEngine

def is_relevant(query, job_title):
    q_words = set(query.lower().split())
    title_words = set(job_title.lower().replace("-", " ").replace("/", " ").split())
    # Relevant if there's significant keyword overlap (at least one core word)
    intersection = q_words.intersection(title_words)
    # Filter out common stop words or prepositions
    meaningful_intersection = intersection.difference({'and', 'or', 'with', 'for', 'in', 'of', 'a', 'an', 'the'})
    return len(meaningful_intersection) > 0

def main():
    print("Initializing Job Description Search evaluation...")
    
    model_dir = r"c:\career iq\models\job_search"
    searcher = JobSearchEngine(model_dir=model_dir)
    
    test_queries = [
        "Data Analyst",
        "Business Analyst",
        "Marketing Data Analyst",
        "Business Intelligence Analyst",
        "Supply Chain Data Analyst"
    ]
    
    p_at_1_list = []
    p_at_3_list = []
    
    detailed_results = []
    
    for q in test_queries:
        results = searcher.search(q, top_k=3)
        
        # Calculate Precision @ 1
        p1 = 1 if is_relevant(q, results[0]['job_title']) else 0
        p_at_1_list.append(p1)
        
        # Calculate Precision @ 3
        relevant_in_top_3 = sum([1 for r in results if is_relevant(q, r['job_title'])])
        p3 = relevant_in_top_3 / 3.0
        p_at_3_list.append(p3)
        
        detailed_results.append({
            "query": q,
            "top_3_results": [
                {
                    "rank": r['rank'],
                    "job_title": r['job_title'],
                    "hybrid_score": r['hybrid_score'],
                    "is_relevant": bool(is_relevant(q, r['job_title']))
                } for r in results
            ],
            "p_at_1": p1,
            "p_at_3": p3
        })
        
    mean_p1 = np.mean(p_at_1_list)
    mean_p3 = np.mean(p_at_3_list)
    
    print("\nEvaluation Results on Test Queries:")
    print(f"  Mean Precision @ 1: {mean_p1*100:.2f}%")
    print(f"  Mean Precision @ 3: {mean_p3*100:.2f}%")
    
    # Save metrics to metrics.json
    metrics_report = {
        "mean_precision_at_1": mean_p1,
        "mean_precision_at_3": mean_p3,
        "detailed_results": detailed_results
    }
    
    metrics_path = os.path.join(model_dir, "metrics.json")
    with open(metrics_path, 'w') as f:
        json.dump(metrics_report, f, indent=2)
        
    print(f"\nSearch evaluation metrics saved to {metrics_path}")

if __name__ == "__main__":
    main()
