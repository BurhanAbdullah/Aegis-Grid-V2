import pandas as pd
import os
from sklearn.metrics import confusion_matrix

# Ensure directories exist
os.makedirs("paper/data", exist_ok=True)
os.makedirs("paper/tables", exist_ok=True)

print("=== EXPORTING REAL PAPER DATA ===")

# Load the real dataset
raw_data_path = "results/final_dataset.csv"
if os.path.exists(raw_data_path):
    df = pd.read_csv(raw_data_path)
    
    # Map 'baseline' to 0 (Normal) and everything else to 1 (Attack)
    df["y_true"] = df["attack"].apply(lambda x: 0 if str(x).lower() == 'baseline' else 1)
    
    # 'consensus' is the agent decision (1 for alert, 0 for normal)
    df["y_pred"] = df["consensus"].astype(int)
    
    # Save the normalized dataset for the paper
    df.to_csv("paper/data/final_dataset_labeled.csv", index=False)
    print("[OK] Labeled dataset generated at paper/data/final_dataset_labeled.csv")

    # Generate Confusion Matrix
    cm = confusion_matrix(df["y_true"], df["y_pred"])
    cm_df = pd.DataFrame(cm, 
                         index=['Actual_Normal', 'Actual_Attack'], 
                         columns=['Predicted_Normal', 'Predicted_Attack'])
    cm_df.to_csv("paper/tables/confusion_matrix.csv")
    print("[OK] Confusion matrix generated at paper/tables/confusion_matrix.csv")

    # Generate Main Metrics Summary Table
    # Re-calculating from the actual labels for 100% accuracy
    tp = cm[1, 1]
    tn = cm[0, 0]
    fp = cm[0, 1]
    fn = cm[1, 0]
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    metrics = pd.DataFrame([{
        "Metric": ["Precision", "Recall", "F1-Score"],
        "Value": [precision, recall, f1]
    }])
    metrics.to_csv("paper/tables/main_results.csv", index=False)
    print("[OK] Performance metrics updated.")
else:
    print("[ERROR] results/final_dataset.csv not found!")

