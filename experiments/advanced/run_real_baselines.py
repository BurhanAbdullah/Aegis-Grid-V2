#!/usr/bin/env python3

import pandas as pd

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score
)

# =====================================================
# LOAD REAL DATASET
# =====================================================

df = pd.read_csv(
    "paper/data/final_dataset_labeled.csv"
)

y_true = df["attack_label"]

# =====================================================
# REAL DETECTOR DEFINITIONS
# =====================================================

systems = {
    "physics_only":
        df["auditor_vote"],

    "communication_only":
        (
            (
                df["monitor_vote"] +
                df["protector_vote"]
            ) > 0
        ).astype(int),

    "consensus_fusion":
        df["prediction_label"]
}

# =====================================================
# COMPUTE METRICS
# =====================================================

rows = []

for name, pred in systems.items():

    rows.append({

        "system": name,

        "precision":
            precision_score(
                y_true,
                pred,
                zero_division=0
            ),

        "recall":
            recall_score(
                y_true,
                pred,
                zero_division=0
            ),

        "f1":
            f1_score(
                y_true,
                pred,
                zero_division=0
            )
    })

out = pd.DataFrame(rows)

out.to_csv(
    "paper/data/advanced/baseline_comparison.csv",
    index=False
)

print(out)
