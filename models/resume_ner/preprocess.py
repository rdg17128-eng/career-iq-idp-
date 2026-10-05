import os
import json
from sklearn.model_selection import train_test_split

def main():
    print("Starting preprocessing for resume NER dataset...")
    
    input_json = r"c:\career iq\datasets\resume_ner_dataset\train\train_data.json"
    if not os.path.exists(input_json):
        print(f"Error: Input file {input_json} does not exist.")
        return
        
    # Read raw JSON
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Loaded {len(data)} NER samples.")
    
    # Collect unique entity types
    entity_types = set()
    for item in data:
        for ent in item.get('entities', []):
            if len(ent) >= 3:
                entity_types.add(ent[2])
                
    entity_types = sorted(list(entity_types))
    print(f"Unique base entity types found: {entity_types}")
    
    # Create BIO tags list
    bio_tags = ["O"]
    for ent_type in entity_types:
        bio_tags.append(f"B-{ent_type}")
        bio_tags.append(f"I-{ent_type}")
        
    label_to_id = {tag: i for i, tag in enumerate(bio_tags)}
    id_to_label = {i: tag for i, tag in enumerate(bio_tags)}
    
    # Create output directories
    output_dir = r"c:\career iq\preprocessing\splits\ner"
    model_dir = r"c:\career iq\models\resume_ner"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(model_dir, exist_ok=True)
    
    # Save label map
    label_map_path = os.path.join(model_dir, "label_map.json")
    with open(label_map_path, 'w') as f:
        json.dump({"label_to_id": label_to_id, "id_to_label": id_to_label}, f, indent=2)
    with open(os.path.join(output_dir, "label_map.json"), 'w') as f:
        json.dump({"label_to_id": label_to_id, "id_to_label": id_to_label}, f, indent=2)
    print(f"Saved BIO label map with {len(bio_tags)} tags to {label_map_path}.")
    
    # Train/Val/Test split: 80% train, 10% val, 10% test (using seed 42)
    train_data, temp_data = train_test_split(data, test_size=0.20, random_state=42)
    val_data, test_data = train_test_split(temp_data, test_size=0.50, random_state=42)
    
    print(f"Split sizes:")
    print(f"  Train: {len(train_data)} samples")
    print(f"  Validation: {len(val_data)} samples")
    print(f"  Test: {len(test_data)} samples")
    
    # Save splits
    with open(os.path.join(output_dir, "train.json"), 'w', encoding='utf-8') as f:
        json.dump(train_data, f, indent=2)
    with open(os.path.join(output_dir, "val.json"), 'w', encoding='utf-8') as f:
        json.dump(val_data, f, indent=2)
    with open(os.path.join(output_dir, "test.json"), 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2)
        
    print("NER Preprocessing completed successfully.")

if __name__ == "__main__":
    main()
