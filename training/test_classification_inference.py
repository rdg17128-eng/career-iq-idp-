import os
import json
import joblib
import numpy as np

def softmax(x):
    e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e_x / e_x.sum(axis=-1, keepdims=True)

class ResumeClassifier:
    def __init__(self, model_dir=r"c:\CareerMind_AI\models\resume_classification"):
        self.model_dir = model_dir
        pipeline_path = os.path.join(model_dir, "classification_pipeline.joblib")
        
        # Load model pipeline
        self.pipeline = joblib.load(pipeline_path)
        
        # Load label map
        with open(os.path.join(model_dir, "label_map.json"), "r") as f:
            label_data = json.load(f)
        self.id_to_label = {int(k): v for k, v in label_data['id_to_label'].items()}
        
    def predict(self, resume_text):
        # Light cleaning
        cleaned_text = " ".join(str(resume_text).replace("\r", " ").replace("\n", " ").split())
        
        # Predict decision function scores
        decision_scores = self.pipeline.decision_function([cleaned_text])
        
        # Convert decision function scores to pseudo-probabilities via softmax
        probs = softmax(decision_scores)[0]
        
        top_idx = np.argmax(probs)
        category = self.id_to_label[top_idx]
        confidence = probs[top_idx]
        
        return category, confidence

def main():
    print("Initializing inference tester...")
    classifier = ResumeClassifier()
    
    # Test cases
    test_cases = [
        {
            "name": "Software Developer Resume",
            "text": "John Doe - Software Engineer. Experience: 4 years building web applications. Technical Skills: Python, Django, Javascript, React, SQL, HTML, CSS. Managed Git repositories and CI/CD pipelines on AWS. Completed BS in Computer Science."
        },
        {
            "name": "Accountant Resume",
            "text": "Jane Smith - Certified Public Accountant (CPA). 5 years in corporate accounting. Expertise in balance sheet preparation, tax audit procedures, accounts payable, ledger reconciliation, QuickBooks, and GAAP standards."
        },
        {
            "name": "HR Specialist Resume",
            "text": "Alice Johnson - HR Manager. 6 years experience in recruitment, staff onboarding, employee relations, policy compliance, conflict resolution, performance appraisal, and compensation/benefits administration."
        }
    ]
    
    print("\nRunning inference tests:")
    print("=" * 60)
    for case in test_cases:
        name = case["name"]
        text = case["text"]
        cat, conf = classifier.predict(text)
        print(f"Test Resume: {name}")
        print(f"Predicted Category: {cat}")
        print(f"Confidence Score:   {conf * 100:.2f}%")
        print("-" * 60)

if __name__ == "__main__":
    main()

