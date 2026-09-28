import os
import shutil
import pandas as pd
import torch
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.replace("\r", " ").replace("\n", " ")
    return " ".join(text.split())

def main():
    print("Initializing Job Description Search indexing...")
    
    # Paths
    src_csv = r"c:\CareerMind_AI\datasets\job_description_dataset\data.csv"
    model_dir = r"c:\CareerMind_AI\models\job_search"
    
    if not os.path.exists(src_csv):
        print(f"Error: Source dataset not found at {src_csv}")
        return
        
    os.makedirs(model_dir, exist_ok=True)
    dest_csv = os.path.join(model_dir, "data.csv")
    
    # Copy dataset file locally
    print(f"Copying dataset to {dest_csv}...")
    shutil.copy(src_csv, dest_csv)
    
    # Load dataset
    df = pd.read_csv(dest_csv)
    print(f"Loaded {len(df)} job descriptions.")
    
    # Clean texts
    descriptions_clean = df['Description'].fillna('').apply(clean_text).tolist()
    
    # -------------------------------------------------------------------------
    # 1. Fit TF-IDF indexer
    # -------------------------------------------------------------------------
    print("Fitting TF-IDF Vectorizer...")
    vectorizer = TfidfVectorizer(max_features=10000, stop_words='english', ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(descriptions_clean)
    
    # Save TF-IDF objects
    vectorizer_path = os.path.join(model_dir, "tfidf_vectorizer.joblib")
    tfidf_index_path = os.path.join(model_dir, "tfidf_index.joblib")
    
    print(f"Saving TF-IDF vectorizer to {vectorizer_path}...")
    joblib.dump(vectorizer, vectorizer_path)
    
    print(f"Saving TF-IDF index matrix to {tfidf_index_path}...")
    joblib.dump(tfidf_matrix, tfidf_index_path)
    
    # -------------------------------------------------------------------------
    # 2. Fit Sentence-BERT indexer
    # -------------------------------------------------------------------------
    print("Loading Sentence-BERT model (all-MiniLM-L6-v2)...")
    sbert = SentenceTransformer('all-MiniLM-L6-v2')
    if torch.cuda.is_available():
        sbert = sbert.to('cuda')
        print("SBERT running on: GPU")
    else:
        print("SBERT running on: CPU")
        
    print("Computing SBERT embeddings for all job descriptions...")
    sbert_embeddings = sbert.encode(
        descriptions_clean,
        convert_to_numpy=True,
        show_progress_bar=True
    )
    
    # Save SBERT index
    sbert_index_path = os.path.join(model_dir, "sbert_index.joblib")
    print(f"Saving SBERT index embeddings to {sbert_index_path}...")
    joblib.dump(sbert_embeddings, sbert_index_path)
    
    print("Job Description Search indexing completed successfully!")

if __name__ == "__main__":
    main()
