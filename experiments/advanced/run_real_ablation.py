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

configs = {

    "full_system":
        df["y_pred"].astype(int),

    "no_physics":
        (
            df["jitter_detected"]
        ).astype(int),

    "no_communication":
        (
            df["kalman_anomaly"] |
            df["cusum_alarm"]
        ).astype(int),

    "no_sequential":
        (
            df["kalman_anomaly"] |
            df["jitter_detected"]
        ).astype(int),

    "consensus_only":
        df["consensus"].astype(int)
}

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
