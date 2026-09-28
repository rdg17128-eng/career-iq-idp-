import os
import json
import joblib
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

def softmax(x):
    e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e_x / e_x.sum(axis=-1, keepdims=True)

class ResumeClassifier:
    def __init__(self, model_dir=None):
        if model_dir is None:
            model_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_dir = model_dir
        
        # Load label map
        label_map_file = os.path.join(model_dir, "label_map.json")
        with open(label_map_file, 'r') as f:
            label_data = json.load(f)
        self.id_to_label = {int(k): v for k, v in label_data['id_to_label'].items()}
        
        # Load optimal model strategy config
        ensemble_config_file = os.path.join(model_dir, "ensemble", "ensemble_config.json")
        if os.path.exists(ensemble_config_file):
            with open(ensemble_config_file, 'r') as f:
                config = json.load(f)
            self.strategy = config.get("best_model_strategy", "ensemble")
        else:
            self.strategy = "ensemble"
            
        print(f"[Classification Inference] Initializing classifier with strategy: {self.strategy.upper()}")
        
        # Load SVM if needed
        self.svm_pipeline = None
        if self.strategy in ["svm", "ensemble"]:
            svm_path = os.path.join(model_dir, "tfidf_svm", "classification_pipeline.joblib")
            print(f"  - Loading SVM from {svm_path}")
            self.svm_pipeline = joblib.load(svm_path)
            
        # Load Transformer if needed
        self.tokenizer = None
        self.bert_model = None
        self.device = None
        if self.strategy in ["transformer", "ensemble"]:
            bert_path = os.path.join(model_dir, "transformer")
            print(f"  - Loading Transformer from {bert_path}")
            self.tokenizer = AutoTokenizer.from_pretrained(bert_path)
            self.bert_model = AutoModelForSequenceClassification.from_pretrained(bert_path)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.bert_model.to(self.device)
            self.bert_model.eval()
            print(f"    (Transformer running on: {self.device})")

    def predict(self, text):
        # Light cleaning
        cleaned_text = " ".join(str(text).replace("\r", " ").replace("\n", " ").split())
        
        svm_probs = None
        bert_probs = None
        
        # Get SVM prediction probabilities
        if self.svm_pipeline is not None:
            svm_decision = self.svm_pipeline.decision_function([cleaned_text])
            svm_probs = softmax(svm_decision)[0]
            
        # Get Transformer prediction probabilities
        if self.bert_model is not None:
            encodings = self.tokenizer(
                [cleaned_text],
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors='pt'
            ).to(self.device)
            with torch.no_grad():
                outputs = self.bert_model(**encodings)
                logits = outputs.logits.cpu().numpy()
                bert_probs = softmax(logits)[0]
                
        # Combine probabilities based on strategy
        if self.strategy == "ensemble":
            # Equal weighting soft voting
            final_probs = 0.5 * svm_probs + 0.5 * bert_probs
        elif self.strategy == "transformer":
            final_probs = bert_probs
        else:
            final_probs = svm_probs
            
        top_idx = np.argmax(final_probs)
        category = self.id_to_label[top_idx]
        confidence = float(final_probs[top_idx])
        
        return category, confidence

def main():
    classifier = ResumeClassifier()
    
    test_cases = [
        {
            "name": "Software Developer",
            "text": "John Doe - Software Engineer. Experience: 4 years building web applications. Technical Skills: Python, Django, Javascript, React, SQL, HTML, CSS. Managed Git repositories and CI/CD pipelines on AWS. Completed BS in Computer Science."
        },
        {
            "name": "Accountant",
            "text": "Jane Smith - Certified Public Accountant (CPA). 5 years in corporate accounting. Expertise in balance sheet preparation, tax audit procedures, accounts payable, ledger reconciliation, QuickBooks, and GAAP standards."
        },
        {
            "name": "HR Specialist",
            "text": "Alice Johnson - HR Manager. 6 years experience in recruitment, staff onboarding, employee relations, policy compliance, conflict resolution, performance appraisal, and compensation/benefits administration."
        }
    ]
    
    print("\nRunning inference tests:")
    print("=" * 60)
    for case in test_cases:
        cat, conf = classifier.predict(case["text"])
        print(f"Test Resume: {case['name']}")
        print(f"Predicted Category: {cat}")
        print(f"Confidence Score:   {conf * 100:.2f}%")
        print("-" * 60)

if __name__ == "__main__":
    main()
