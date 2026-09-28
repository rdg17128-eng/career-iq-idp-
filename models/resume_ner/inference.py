import os
import torch
from transformers import pipeline

class ResumeNERExtractor:
    def __init__(self, model_dir=None):
        if model_dir is None:
            # Dynamically resolve directory where this script is located
            model_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_dir = model_dir
        
        # Check GPU availability
        device = 0 if torch.cuda.is_available() else -1
        print(f"[NER Inference] Loading model from: {model_dir} (Device: {'GPU' if device == 0 else 'CPU'})")
        
        # Use aggregation_strategy="simple" to group adjacent B- and I- tokens
        self.nlp = pipeline(
            "token-classification",
            model=model_dir,
            tokenizer=model_dir,
            aggregation_strategy="simple",
            device=device
        )
        
    def extract_entities(self, text):
        results = self.nlp(text)
        extracted = []
        for r in results:
            extracted.append({
                'entity': r['entity_group'],
                'text': r['word'].strip(),
                'confidence': float(r['score']),
                'start': r['start'],
                'end': r['end']
            })
        return extracted

def main():
    extractor = ResumeNERExtractor()
    
    test_text = (
        "Alice Clark - Senior Software Engineer at Google. "
        "Education: Bachelor of Science in Computer Science from Stanford University (graduated 2018). "
        "Technical Skills: Python, Java, Docker, Kubernetes, machine learning. "
        "Contact: alice.smith@email.com. Location: San Francisco, CA. "
        "Experienced in backend development for 5 years."
    )
    
    print("\nAnalyzing test resume text:")
    print("=" * 60)
    print(test_text)
    print("=" * 60)
    
    entities = extractor.extract_entities(test_text)
    
    print(f"\nExtracted {len(entities)} entities:")
    for ent in entities:
        print(f"  - Entity: {ent['entity']:<20} | Text: {ent['text']:<30} | Confidence: {ent['confidence']*100:.1f}%")
    print("=" * 60)

if __name__ == "__main__":
    main()
