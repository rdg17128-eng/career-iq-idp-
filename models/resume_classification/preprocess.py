import os
import pandas as pd
import json
from sklearn.model_selection import train_test_split

def clean_text(text):
    if not isinstance(text, str):
        return ""
    # Standard light cleaning
    text = text.replace("\r", " ").replace("\n", " ")
    # Replace multiple spaces with a single space
    text = " ".join(text.split())
    return text

def main():
    print("Starting preprocessing for resume classification dataset...")
    
    input_csv = r"c:\career iq\datasets\resume_classification_dataset\Resume\Resume.csv"
    if not os.path.exists(input_csv):
        print(f"Error: Input file {input_csv} does not exist.")
        return
        
    # Read the dataset
    df = pd.read_csv(input_csv)
    print(f"Original dataset shape: {df.shape}")
    
    # Preprocess text and labels
    df['clean_text'] = df['Resume_str'].apply(clean_text)
    df = df[df['clean_text'].str.strip() != '']
    df = df[df['Category'].notnull()]
    
    print(f"Shape after filtering empty texts: {df.shape}")
    
    # Label encoding
    categories = sorted(df['Category'].unique())
    label_to_id = {cat: i for i, cat in enumerate(categories)}
    id_to_label = {i: cat for i, cat in enumerate(categories)}
    
    df['label'] = df['Category'].map(label_to_id)
    
    # Ensure save directory exists
    output_dir = r"c:\career iq\preprocessing\splits\classification"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save label map to model dir and preprocessing splits dir
    model_dir = r"c:\career iq\models\resume_classification"
    os.makedirs(model_dir, exist_ok=True)
    
    with open(os.path.join(model_dir, "label_map.json"), "w") as f:
        json.dump({"label_to_id": label_to_id, "id_to_label": id_to_label}, f, indent=2)
    with open(os.path.join(output_dir, "label_map.json"), "w") as f:
        json.dump({"label_to_id": label_to_id, "id_to_label": id_to_label}, f, indent=2)
        
    print(f"Label map saved with {len(categories)} classes.")
    
    # Train/Val/Test split: 80% train, 10% val, 10% test
    # We use stratification since some categories have low sample sizes (like BPO, AUTOMOBILE)
    train_df, temp_df = train_test_split(
        df, test_size=0.20, random_state=42, stratify=df['label']
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.50, random_state=42, stratify=temp_df['label']
    )
    
    print(f"Splits generated:")
    print(f"  Train: {train_df.shape[0]} rows")
    print(f"  Validation: {val_df.shape[0]} rows")
    print(f"  Test: {test_df.shape[0]} rows")
    
    # Save splits
    train_df[['clean_text', 'label']].to_csv(os.path.join(output_dir, "train.csv"), index=False)
    val_df[['clean_text', 'label']].to_csv(os.path.join(output_dir, "val.csv"), index=False)
    test_df[['clean_text', 'label']].to_csv(os.path.join(output_dir, "test.csv"), index=False)
    
    print("Preprocessing completed and split files saved successfully.")

if __name__ == "__main__":
    main()
