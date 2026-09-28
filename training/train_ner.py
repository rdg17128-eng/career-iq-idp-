import os
import json
import torch
import numpy as np
from torch.utils.data import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    Trainer,
    TrainingArguments,
    DataCollatorForTokenClassification
)
from seqeval.metrics import f1_score, precision_score, recall_score, accuracy_score

class NERDataset(Dataset):
    def __init__(self, json_file, tokenizer, label_to_id, max_len=512):
        with open(json_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.tokenizer = tokenizer
        self.label_to_id = label_to_id
        self.max_len = max_len
        
        self.features = []
        self._preprocess()
        
    def _preprocess(self):
        print(f"Aligning and pre-tokenizing {len(self.data)} NER samples with sliding window...")
        for idx, item in enumerate(self.data):
            text = item.get('text', '')
            entities = item.get('entities', [])
            
            # Tokenize using sliding window with stride of 64 tokens
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

from transformers import EarlyStoppingCallback

def main():
    print("Loading NER training configuration...")
    splits_dir = r"c:\CareerMind_AI\preprocessing\splits\ner"
    model_dir = r"c:\CareerMind_AI\models\resume_ner"
    
    train_json = os.path.join(splits_dir, "train.json")
    val_json = os.path.join(splits_dir, "val.json")
    label_map_file = os.path.join(model_dir, "label_map.json")
    
    if not (os.path.exists(train_json) and os.path.exists(val_json) and os.path.exists(label_map_file)):
        print("Error: NER splits or label map not found. Please run preprocessing first.")
        return
        
    with open(label_map_file, 'r') as f:
        label_data = json.load(f)
    label_to_id = label_data['label_to_id']
    id_to_label = {int(k): v for k, v in label_data['id_to_label'].items()}
    num_labels = len(label_to_id)
    
    # Model configuration (RoBERTa fine-tuned on GPU)
    model_name = "roberta-base"
    tokenizer = AutoTokenizer.from_pretrained(model_name, add_prefix_space=True)
    model = AutoModelForTokenClassification.from_pretrained(
        model_name,
        num_labels=num_labels,
        id2label=id_to_label,
        label2id=label_to_id
    )
    
    # We will do full fine-tuning of all parameters since we are training on GPU
    print("Full fine-tuning of all RoBERTa encoder weights...")
    for param in model.parameters():
        param.requires_grad = True
        
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Trainable parameters: {trainable_params:,} / {total_params:,} total.")
    
    # Datasets
    train_dataset = NERDataset(train_json, tokenizer, label_to_id, max_len=512)
    val_dataset = NERDataset(val_json, tokenizer, label_to_id, max_len=512)
    
    def compute_metrics(p):
        predictions, labels = p
        predictions = np.argmax(predictions, axis=2)
        
        true_predictions = [
            [id_to_label[p] for (p, l) in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, labels)
        ]
        true_labels = [
            [id_to_label[l] for (p, l) in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, labels)
        ]
        
        return {
            "precision": precision_score(true_labels, true_predictions),
            "recall": recall_score(true_labels, true_predictions),
            "f1": f1_score(true_labels, true_predictions),
            "accuracy": accuracy_score(true_labels, true_predictions)
        }
        
    training_args = TrainingArguments(
        output_dir=os.path.join(model_dir, "checkpoints"),
        num_train_epochs=25,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        gradient_accumulation_steps=2,
        fp16=True,
        warmup_steps=40,
        weight_decay=0.01,
        logging_steps=10,
        eval_strategy="steps",
        eval_steps=10,
        save_strategy="steps",
        save_steps=10,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        learning_rate=3e-5,
        report_to="none"
    )
    
    data_collator = DataCollatorForTokenClassification(tokenizer)
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=5)]
    )
    
    print("Training NER model...")
    train_result = trainer.train()
    metrics = train_result.metrics
    
    print("Evaluating NER model on validation set...")
    eval_results = trainer.evaluate()
    for k, v in eval_results.items():
        print(f"  {k}: {v}")
        
    # Combine training and evaluation metrics
    combined_metrics = {
        "train_metrics": metrics,
        "eval_metrics": eval_results
    }
    metrics_path = os.path.join(model_dir, "training_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(combined_metrics, f, indent=2)
    print(f"Training and evaluation metrics saved to {metrics_path}")
        
    print(f"Saving final trained model to {model_dir}...")
    trainer.save_model(model_dir)
    tokenizer.save_pretrained(model_dir)
    print("NER Model saved successfully!")

if __name__ == "__main__":
    main()

