#!/usr/bin/env python3

import os
import shutil
import pandas as pd

EXPORTS = {
    # ROC
    "results/roc_metrics.csv":
        "paper/data/roc_metrics.csv",

    "plotting_data/roc_curve_data.csv":
        "paper/data/roc_curve_data.csv",

    # Detector outputs
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

    # Validation
    "results/csv/monte_carlo_results.csv":
        "paper/data/monte_carlo_results.csv",

    "results/csv/stealth_sweep.csv":
        "paper/data/stealth_sweep.csv",

    "results/csv/scaling_results.csv":
        "paper/data/scaling_results.csv",

    # Final dataset
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

print("\nExport complete.")

# =====================================================
# AUTO-GENERATE CONFUSION MATRIX TABLE
# =====================================================

dataset_path = "results/final_dataset.csv"

if os.path.exists(dataset_path):

    df = pd.read_csv(dataset_path)

    required = {"y_true", "y_pred"}

    if required.issubset(df.columns):

        tp = ((df.y_true == 1) & (df.y_pred == 1)).sum()
        tn = ((df.y_true == 0) & (df.y_pred == 0)).sum()
        fp = ((df.y_true == 0) & (df.y_pred == 1)).sum()
        fn = ((df.y_true == 1) & (df.y_pred == 0)).sum()

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

    else:
        print("[SKIP] final_dataset.csv missing y_true/y_pred")

# =====================================================
# AUTO-GENERATE METRIC TABLE
# =====================================================

roc_path = "results/roc_metrics.csv"

if os.path.exists(roc_path):

    roc = pd.read_csv(roc_path)

    roc.to_csv(
        "paper/tables/main_results.csv",
        index=False
    )

    print("[OK] main_results.csv generated")
