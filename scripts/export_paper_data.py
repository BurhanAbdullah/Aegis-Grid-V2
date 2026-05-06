#!/usr/bin/env python3

import os
import shutil
import pandas as pd
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score

EXPORTS = {

    "results/roc_metrics.csv":
        "paper/data/roc_metrics.csv",

    "plotting_data/roc_curve_data.csv":
        "paper/data/roc_curve_data.csv",

    "plotting_data/nis_values.csv":
        "paper/data/nis_values.csv",

    "plotting_data/jitter_values.csv":
        "paper/data/jitter_values.csv",

    "plotting_data/cusum_values.csv":
        "paper/data/cusum_values.csv",

    "plotting_data/consensus_votes.csv":
        "paper/data/consensus_votes.csv",

    "plotting_data/pf_behavior.csv":
        "paper/data/pf_behavior.csv",

    "results/csv/monte_carlo_results.csv":
        "paper/data/monte_carlo_results.csv",

    "results/csv/stealth_sweep.csv":
        "paper/data/stealth_sweep.csv",

    "results/csv/scaling_results.csv":
        "paper/data/scaling_results.csv",

    "results/final_dataset.csv":
        "paper/data/final_dataset.csv",
}

print("\n=== EXPORTING REAL PAPER DATA ===")

for src, dst in EXPORTS.items():

    if os.path.exists(src):

        os.makedirs(os.path.dirname(dst), exist_ok=True)

        shutil.copy2(src, dst)

        print(f"[OK] {src} -> {dst}")

    else:
        print(f"[MISSING] {src}")

# =====================================================
# LOAD FINAL DATASET
# =====================================================

dataset_path = "results/final_dataset.csv"

if not os.path.exists(dataset_path):

    raise FileNotFoundError(dataset_path)

df = pd.read_csv(dataset_path)

# =====================================================
# NORMALIZE LABELS
# =====================================================

# Ground truth:
# attack column indicates actual attack existence

df["y_true"] = df["attack"].astype(int)

# Prediction:
# consensus indicates system detection decision

df["y_pred"] = df["consensus"].astype(int)

# Save normalized dataset

df.to_csv(
    "paper/data/final_dataset_labeled.csv",
    index=False
)

print("[OK] final_dataset_labeled.csv generated")

# =====================================================
# CONFUSION MATRIX
# =====================================================

tn, fp, fn, tp = confusion_matrix(
    df["y_true"],
    df["y_pred"]
).ravel()

cm = pd.DataFrame([{
    "tn": tn,
    "fp": fp,
    "fn": fn,
    "tp": tp
}])

cm.to_csv(
    "paper/tables/confusion_matrix.csv",
    index=False
)

print("[OK] confusion_matrix.csv generated")

# =====================================================
# METRIC TABLE
# =====================================================

precision = precision_score(
    df["y_true"],
    df["y_pred"],
    zero_division=0
)

recall = recall_score(
    df["y_true"],
    df["y_pred"],
    zero_division=0
)

f1 = f1_score(
    df["y_true"],
    df["y_pred"],
    zero_division=0
)

metrics = pd.DataFrame([{
    "precision": precision,
    "recall": recall,
    "f1_score": f1
}])

metrics.to_csv(
    "paper/tables/main_results.csv",
    index=False
)

print("[OK] main_results.csv generated")

print("\n=== FINAL METRICS ===")
print(metrics)
