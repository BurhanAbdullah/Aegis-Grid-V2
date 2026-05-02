#!/bin/bash

echo "======================================"
echo "Generating ROC curves from detector data"
echo "======================================"

mkdir -p figures
mkdir -p roc_data

python3 << 'EOF'
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc

# Load experiment dataset
df = pd.read_csv("plotting_data/full_experiment_table.csv")

# Convert mitigation column to binary label
df["label"] = (df["mitigation"] == True).astype(int)

# Build synthetic detector score signals
scores = {}

if "nis" in df.columns:
    scores["NIS"] = df["nis"]

if "cusum_stat" in df.columns:
    scores["CUSUM"] = df["cusum_stat"]

if "jitter_z" in df.columns:
    scores["Jitter"] = df["jitter_z"]

if "threat_score" in df.columns:
    scores["Fusion"] = df["threat_score"]

plt.figure(figsize=(7,7))

for name, signal in scores.items():
    signal = signal.fillna(0)
    fpr, tpr, _ = roc_curve(df["label"], signal)
    roc_auc = auc(fpr, tpr)

    plt.plot(fpr, tpr, label=f"{name} (AUC={roc_auc:.2f})")

    pd.DataFrame({
        "FPR": fpr,
        "TPR": tpr
    }).to_csv(f"roc_data/{name}_roc.csv", index=False)

plt.plot([0,1],[0,1],'k--')

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curves for Multi-Layer Detection Pipeline")
plt.legend()
plt.grid(True)

plt.savefig("figures/roc_curve.png", dpi=300)
print("ROC figure saved to figures/roc_curve.png")

EOF
