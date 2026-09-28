import os
import joblib
import pandas as pd
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.replace("\r", " ").replace("\n", " ")
    return " ".join(text.split())

class JobSearchEngine:
    def __init__(self, model_dir=None):
        if model_dir is None:
            model_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_dir = model_dir
        
        # Paths
        self.db_path = os.path.join(model_dir, "data.csv")
        vectorizer_path = os.path.join(model_dir, "tfidf_vectorizer.joblib")
        tfidf_index_path = os.path.join(model_dir, "tfidf_index.joblib")
        sbert_index_path = os.path.join(model_dir, "sbert_index.joblib")
        
        # Check files
        if not (os.path.exists(self.db_path) and os.path.exists(vectorizer_path) and 
                os.path.exists(tfidf_index_path) and os.path.exists(sbert_index_path)):
            raise FileNotFoundError("Missing one or more index files. Please run train_search.py first.")
            
        # Load database
        self.df = pd.read_csv(self.db_path)
        print(f"[Search Engine] Loaded {len(self.df)} job descriptions database.")
        
        # Load TF-IDF index
        print("[Search Engine] Loading TF-IDF index...")
        self.vectorizer = joblib.load(vectorizer_path)
        self.tfidf_matrix = joblib.load(tfidf_index_path)
        
        # Load SBERT index
        print("[Search Engine] Loading SBERT index...")
        self.sbert_embeddings = joblib.load(sbert_index_path)
        
        # Initialize Sentence-BERT
        print("[Search Engine] Loading Sentence-BERT model (all-MiniLM-L6-v2)...")
        self.sbert = SentenceTransformer('all-MiniLM-L6-v2')
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.sbert = self.sbert.to(self.device)
        print(f"  - SBERT running on: {self.device}")
        
        print("Job Description Search Engine fully initialized!")

    def search(self, query, top_k=5, w_tfidf=0.5, w_sbert=0.5):
        query_clean = clean_text(query)
        
        # 1. TF-IDF Keyword Match
        Q_tfidf = self.vectorizer.transform([query_clean])
        S_tfidf = cosine_similarity(self.tfidf_matrix, Q_tfidf).flatten()
        
        # 2. SBERT Semantic Match
        Q_sbert = self.sbert.encode(query_clean, convert_to_numpy=True)
        # Reshape to 2D array
        Q_sbert_2d = Q_sbert.reshape(1, -1)
        S_sbert = cosine_similarity(self.sbert_embeddings, Q_sbert_2d).flatten()
        
        # 3. Hybrid Combined Score
        S_hybrid = w_tfidf * S_tfidf + w_sbert * S_sbert
        
        # 4. Rank indices
        top_indices = np.argsort(S_hybrid)[::-1][:top_k]
        
        results = []
        for rank, idx in enumerate(top_indices):
            row = self.df.iloc[idx]
            results.append({
                'rank': rank + 1,
                'job_title': row['Job Title'],
                'description': row['Description'],
                'tfidf_score': float(S_tfidf[idx]),
                'sbert_score': float(S_sbert[idx]),
                'hybrid_score': float(S_hybrid[idx])
            })
            
        return results

def main():
    searcher = JobSearchEngine()
    
    test_queries = [
        "python backend software developer",
        "corporate tax accountant or audit specialist",
        "commercial truck driver dispatch operations"
    ]
    
    print("\nRunning search tests:")
    print("=" * 60)
    for q in test_queries:
        print(f"Search Query: '{q}'")
        print("-" * 60)
        results = searcher.search(q, top_k=2)
        
        for res in results:
            print(f"Rank #{res['rank']}: {res['job_title']}")
            print(f"  Hybrid Score: {res['hybrid_score']:.4f} (TF-IDF: {res['tfidf_score']:.4f}, SBERT: {res['sbert_score']:.4f})")
            print(f"  Description snippet: {str(res['description'])[:180]}...")
            print()
        print("=" * 60)

if __name__ == "__main__":
    main()
