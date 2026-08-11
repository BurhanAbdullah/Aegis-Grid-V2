import pandas as pd
import os
import sys
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

# Optional base directory for staging output
out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
paper_data_dir = os.path.join(out_dir, "paper", "data")
paper_tables_dir = os.path.join(out_dir, "paper", "tables")

os.makedirs(paper_data_dir, exist_ok=True)
os.makedirs(paper_tables_dir, exist_ok=True)

print("=== EXPORTING REAL PAPER DATA ===")

raw_data_path = sys.argv[2] if len(sys.argv) > 2 else "results/final_dataset.csv"
if not os.path.exists(raw_data_path) and os.path.exists("data/full_experiment_table.csv"):
    raw_data_path = "data/full_experiment_table.csv"

if os.path.exists(raw_data_path):
    df = pd.read_csv(raw_data_path)
    
    # Ground truth: 'baseline' is 0 (Normal), non-baseline is 1 (Attack)
    df["y_true"] = df["attack"].apply(lambda x: 0 if str(x).lower() == 'baseline' else 1)
    
    # Compute votes from individual binary detectors if present
    if "cusum_alarm" in df.columns and "jitter_detected" in df.columns and "kalman_anomaly" in df.columns:
        df["votes"] = df["cusum_alarm"].astype(int) + df["jitter_detected"].astype(int) + df["kalman_anomaly"].astype(int)
    else:
        df["votes"] = df["consensus"].astype(int)

    # Prediction columns for both quorums
    df["y_pred_k2"] = (df["votes"] >= 2).astype(int)  # Strict majority
    df["y_pred_k1"] = (df["votes"] >= 1).astype(int)  # OR / Sensitivity mode
    
    # Save labeled dataset
    labeled_out = os.path.join(paper_data_dir, "final_dataset_labeled.csv")
    df.to_csv(labeled_out, index=False)
    print(f"[OK] Labeled dataset generated at {labeled_out}")

    metrics_rows = []
    for k_val, col_name, k_label in [(2, "y_pred_k2", "K=2 (Strict Majority)"), (1, "y_pred_k1", "K=1 (OR Mode)")]:
        cm = confusion_matrix(df["y_true"], df[col_name])
        tn, fp, fn, tp = cm.ravel()
        
        cm_df = pd.DataFrame(cm, 
                             index=['Actual_Normal', 'Actual_Attack'], 
                             columns=['Predicted_Normal', 'Predicted_Attack'])
        cm_path = os.path.join(paper_tables_dir, f"confusion_matrix_k{k_val}.csv")
        cm_df.to_csv(cm_path)
        if k_val == 2:
            cm_df.to_csv(os.path.join(paper_tables_dir, "confusion_matrix.csv"))
        
        acc = accuracy_score(df["y_true"], df[col_name])
        prec = precision_score(df["y_true"], df[col_name], zero_division=0)
        rec = recall_score(df["y_true"], df[col_name], zero_division=0)
        f1 = f1_score(df["y_true"], df[col_name], zero_division=0)
        
        metrics_rows.append({
            "Quorum": k_label,
            "TN": tn,
            "FP": fp,
            "FN": fn,
            "TP": tp,
            "Accuracy": acc,
            "Precision": prec,
            "Recall": rec,
            "F1-Score": f1
        })
    
    metrics_df = pd.DataFrame(metrics_rows)
    main_res_path = os.path.join(paper_tables_dir, "main_results.csv")
    metrics_df.to_csv(main_res_path, index=False)
    print(f"[OK] Performance metrics updated at {main_res_path}")
else:
    print(f"[ERROR] {raw_data_path} not found!")


