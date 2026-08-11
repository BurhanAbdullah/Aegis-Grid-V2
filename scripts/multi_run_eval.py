import subprocess
import pandas as pd
import numpy as np
import os
import sys
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score

out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
plot_dir = os.path.join(out_dir, "plotting_data")
os.makedirs(plot_dir, exist_ok=True)

results = []

for i in range(10):
    subprocess.run(["python3", "scripts/generate_realistic_dataset.py"], stdout=subprocess.DEVNULL)

    df = pd.read_csv("data/full_experiment_table.csv")
    y_true = (df['attack'] != 'baseline').astype(int)

    votes = (
        df['kalman_anomaly'].astype(int) +
        (df['cusum_alarm'] == True).astype(int) +
        (df['jitter_detected'] == True).astype(int)
    )

    y_pred_k2 = (votes >= 2).astype(int)
    y_pred_k1 = (votes >= 1).astype(int)

    results.append({
        "run": i + 1,
        "k2_precision": precision_score(y_true, y_pred_k2, zero_division=0),
        "k2_recall": recall_score(y_true, y_pred_k2, zero_division=0),
        "k2_f1": f1_score(y_true, y_pred_k2, zero_division=0),
        "k1_precision": precision_score(y_true, y_pred_k1, zero_division=0),
        "k1_recall": recall_score(y_true, y_pred_k1, zero_division=0),
        "k1_f1": f1_score(y_true, y_pred_k1, zero_division=0),
    })

df_out = pd.DataFrame(results)

print("\n=== MULTI-RUN RESULTS ===")
print(df_out.describe())

out_csv = os.path.join(plot_dir, "multi_run_results.csv")
df_out.to_csv(out_csv, index=False)
print(f"[OK] Multi-run results saved to {out_csv}")

