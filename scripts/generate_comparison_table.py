import sys
import os
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score

base_dir = sys.argv[1] if len(sys.argv) > 1 else "."
input_path = os.path.join(base_dir, "raw", "full_experiment_table.csv")
if not os.path.exists(input_path):
    input_path = os.path.join(base_dir, "data", "full_experiment_table.csv")
if not os.path.exists(input_path):
    input_path = "data/full_experiment_table.csv"

out_dir = os.path.join(base_dir, "plotting_data")
os.makedirs(out_dir, exist_ok=True)

df = pd.read_csv(input_path)

y_true = (df['attack'] != 'baseline').astype(int)

votes = (
    df['kalman_anomaly'].astype(int) +
    (df['cusum_alarm'] == True).astype(int) +
    (df['jitter_detected'] == True).astype(int)
)

def eval_model(name, pred):
    return {
        "method": name,
        "precision": precision_score(y_true, pred, zero_division=0),
        "recall": recall_score(y_true, pred, zero_division=0),
        "f1": f1_score(y_true, pred, zero_division=0)
    }

rows = []

# Quorum consensus methods with explicit quorum labels
rows.append(eval_model("Consensus (K=2, Primary)", (votes >= 2).astype(int)))
rows.append(eval_model("Consensus (K=1, Sensitivity)", (votes >= 1).astype(int)))

# Standalone baselines
rows.append(eval_model("CUSUM",  (df['cusum_alarm'] == True).astype(int)))
rows.append(eval_model("JITTER", (df['jitter_detected'] == True).astype(int)))
rows.append(eval_model("KALMAN", (df['kalman_anomaly'] == True).astype(int)))

pd.DataFrame(rows).to_csv(os.path.join(out_dir, "comparison_table.csv"), index=False)

print("comparison_table.csv generated with explicit K=2 and K=1 consensus entries.")

