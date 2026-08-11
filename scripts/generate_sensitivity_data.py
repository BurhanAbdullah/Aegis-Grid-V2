import sys
import os
import pandas as pd
import numpy as np
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
scores = df['threat_score']

thresholds = np.linspace(scores.min(), scores.max(), 50)

precisions = []
recalls = []
f1s = []

for th in thresholds:
    y_pred = (scores >= th).astype(int)
    p = precision_score(y_true, y_pred, zero_division=0)
    r = recall_score(y_true, y_pred, zero_division=0)
    f = f1_score(y_true, y_pred, zero_division=0)
    precisions.append(p)
    recalls.append(r)
    f1s.append(f)

out = pd.DataFrame({
    "threshold": thresholds,
    "precision": precisions,
    "recall": recalls,
    "f1": f1s
})

out.to_csv(os.path.join(out_dir, "sensitivity_data.csv"), index=False)

print("Sensitivity data generated with precision, recall, and F1.")

