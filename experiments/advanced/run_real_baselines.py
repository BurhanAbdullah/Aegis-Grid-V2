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

y_true = df["y_true"]

systems = {

    "physics_only":
        df["kalman_anomaly"].astype(int),

    "communication_only":
        df["jitter_detected"].astype(int),

    "sequential_only":
        df["cusum_alarm"].astype(int),

    "consensus":
        df["consensus"].astype(int),

    "fusion_final":
        df["y_pred"].astype(int)
}

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
