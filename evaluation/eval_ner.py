import os
import json
import torch
import numpy as np
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModelForTokenClassification, DataCollatorForTokenClassification
from seqeval.metrics import classification_report, f1_score, precision_score, recall_score, accuracy_score
from tqdm import tqdm

class NERDataset(torch.utils.data.Dataset):
    def __init__(self, json_file, tokenizer, label_to_id, max_len=512):
        with open(json_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.tokenizer = tokenizer
        self.label_to_id = label_to_id
        self.max_len = max_len
        
        self.features = []
        self._preprocess()
        
    def _preprocess(self):
        for idx, item in enumerate(self.data):
            text = item.get('text', '')
            entities = item.get('entities', [])
            
            # Tokenize using sliding window with stride of 64 tokens (must match train_ner.py)
            encoding = self.tokenizer(
                text,
                max_length=self.max_len,
                padding='max_length',
                truncation=True,
                stride=64,
                return_overflowing_tokens=True,
                return_offsets_mapping=True,
                return_tensors='pt'
            )
            
            num_chunks = len(encoding['input_ids'])
            for chunk_idx in range(num_chunks):
                input_ids = encoding['input_ids'][chunk_idx]
                attention_mask = encoding['attention_mask'][chunk_idx]
                offset_mapping = encoding['offset_mapping'][chunk_idx].tolist()
                sequence_ids = encoding.sequence_ids(chunk_idx)
                word_ids = encoding.word_ids(chunk_idx)
                
                # Align labels
                labels = []
                previous_word_idx = None
                for i, (start, end) in enumerate(offset_mapping):
                    word_idx = word_ids[i]
                    if sequence_ids[i] is None or word_idx is None:
                        # Special token
                        labels.append(-100)
                    elif word_idx == previous_word_idx:
                        # Subsequent subword of the same word -> ignore (label as -100)
                        labels.append(-100)
                    else:
                        # First subword of a new word -> assign label
                        assigned_label = self.label_to_id["O"]
                        for ent_start, ent_end, ent_label in entities:
                            # Robust overlap-based condition
                            overlap_start = max(start, ent_start)
                            overlap_end = min(end, ent_end)
                            if overlap_start < overlap_end:
                                # This token overlaps the entity
                                is_b = False
                                if start <= ent_start < end:
                                    is_b = True
                                else:
                                    # Check if any previous token in this chunk overlaps this entity
                                    has_prev_overlap = False
                                    for prev_i in range(i):
                                        prev_start, prev_end = offset_mapping[prev_i]
                                        if max(prev_start, ent_start) < min(prev_end, ent_end):
                                            has_prev_overlap = True
                                            break
                                    if not has_prev_overlap:
                                        is_b = True
                                
                                if is_b:
                                    assigned_label = self.label_to_id[f"B-{ent_label}"]
                                else:
                                    assigned_label = self.label_to_id[f"I-{ent_label}"]
                                break
                        labels.append(assigned_label)
                        previous_word_idx = word_idx
                
                self.features.append({
                    'input_ids': input_ids,
                    'attention_mask': attention_mask,
                    'labels': torch.tensor(labels, dtype=torch.long)
                })
            
    def __len__(self):
        return len(self.features)
        
    def __getitem__(self, index):
        return self.features[index]

def main():
    print("Loading NER model and test dataset for evaluation...")
    model_dir = r"c:\CareerMind_AI\models\resume_ner"
    test_json = r"c:\CareerMind_AI\preprocessing\splits\ner\test.json"
    
    if not (os.path.exists(model_dir) and os.path.exists(test_json)):
        print("Error: NER model directory or test dataset not found.")
        return
        
    # Load label map
    label_map_file = os.path.join(model_dir, "label_map.json")
    with open(label_map_file, 'r') as f:
        label_data = json.load(f)
    label_to_id = label_data['label_to_id']
    id_to_label = {int(k): v for k, v in label_data['id_to_label'].items()}
    
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForTokenClassification.from_pretrained(model_dir)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    model.to(device)
    model.eval()
    
    dataset = NERDataset(test_json, tokenizer, label_to_id, max_len=512)
    data_collator = DataCollatorForTokenClassification(tokenizer)
    dataloader = DataLoader(dataset, batch_size=8, shuffle=False, collate_fn=data_collator)
    
    all_preds = []
    all_labels = []
    
    print("Running inference on NER test dataset...")
    with torch.no_grad():
        for batch in tqdm(dataloader):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels']
            
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            
            preds = torch.argmax(logits, dim=2).cpu().numpy()
            
            for pred, label in zip(preds, labels.numpy()):
                # Filter out special tokens (-100)
                pred_list = [id_to_label[p] for (p, l) in zip(pred, label) if l != -100]
                label_list = [id_to_label[l] for (p, l) in zip(pred, label) if l != -100]
                all_preds.append(pred_list)
                all_labels.append(label_list)
                
    # Calculate metrics
    precision = precision_score(all_labels, all_preds)
    recall = recall_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds)
    accuracy = accuracy_score(all_labels, all_preds)
    
    print(f"\nEvaluation Summary:")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1 Score:  {f1:.4f}")
    print(f"  Accuracy:  {accuracy:.4f}")
    
    print("\nClassification Report by Entity Type:")
    report_str = classification_report(all_labels, all_preds, zero_division=0)
    print(report_str)
    
    # Save to metrics file
    report_dict = {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": accuracy,
        "report": report_str
    }
    
    metrics_path = os.path.join(model_dir, "evaluation_metrics.json")
    with open(metrics_path, 'w') as f:
        json.dump(report_dict, f, indent=2)
    print(f"NER evaluation metrics saved to {metrics_path}")

if __name__ == "__main__":
    main()
