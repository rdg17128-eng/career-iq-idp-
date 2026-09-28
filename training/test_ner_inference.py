import os
import torch
from transformers import pipeline

class ResumeNERExtractor:
    def __init__(self, model_dir=r"c:\CareerMind_AI\models\resume_ner"):
        self.model_dir = model_dir
        # Detect and use GPU if available
        device = 0 if torch.cuda.is_available() else -1
        # Use aggregation_strategy="simple" to group adjacent tokens of same entity class
        self.nlp = pipeline(
            "token-classification",
            model=model_dir,
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
    print("Initializing NER inference tester...")
    extractor = ResumeNERExtractor()
    
    test_text = (
        "Alice Smith - Senior Software Engineer at Google. "
        "Education: Bachelor of Science in Computer Science from Stanford University (graduated 2018). "
        "Technical Skills: Python, Java, Docker, Kubernetes, machine learning. "
        "Contact: alice.smith@email.com. Location: San Francisco, CA. "
        "Experienced in backend development for 5 years."
    )
    
    print(f"\nAnalyzing test resume text:\n\"{test_text}\"\n")
    print("=" * 60)
    entities = extractor.extract_entities(test_text)
    
    # Sort entities by their type or start offset
    print(f"Extracted {len(entities)} entities:")
    for ent in entities:
        print(f"  - Entity: {ent['entity']:<20} | Text: {ent['text']:<30} | Confidence: {ent['confidence']*100:.1f}%")
    print("=" * 60)

if __name__ == "__main__":
    main()
