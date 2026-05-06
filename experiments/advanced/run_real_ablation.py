#!/usr/bin/env python3

import pandas as pd

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score
)

df = pd.read_csv(
    "paper/data/final_dataset_labeled.csv"
)

y_true = df["attack_label"]

# =====================================================
# REAL CONFIGURATIONS
# =====================================================

configs = {

    "full_system":
        df["prediction_label"],

    "no_sequential":
        (
            (
                df["monitor_vote"] +
                df["protector_vote"]
            ) >= 2
        ).astype(int),

    "communication_only":
        (
            (
                df["monitor_vote"] +
                df["protector_vote"]
            ) > 0
        ).astype(int),

    "physics_only":
        df["auditor_vote"],

    "monitor_only":
        df["monitor_vote"],

    "protector_only":
        df["protector_vote"]
}

# =====================================================
# METRICS
# =====================================================

rows = []

for name, pred in configs.items():

    rows.append({

        "configuration": name,

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
    "paper/data/advanced/ablation_study.csv",
    index=False
)

print(out)
