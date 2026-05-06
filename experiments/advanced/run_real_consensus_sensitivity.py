#!/usr/bin/env python3

import pandas as pd

from sklearn.metrics import (
    precision_score,
    recall_score
)

df = pd.read_csv(
    "paper/data/final_dataset_labeled.csv"
)

y_true = df["y_true"]

votes = (
    df["kalman_anomaly"].astype(int)
    + df["jitter_detected"].astype(int)
    + df["cusum_alarm"].astype(int)
)

rows = []

for quorum in [1, 2, 3]:

    pred = (
        votes >= quorum
    ).astype(int)

    rows.append({

        "quorum": quorum,

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
            )
    })

out = pd.DataFrame(rows)

out.to_csv(
    "paper/data/advanced/consensus_sensitivity.csv",
    index=False
)

print(out)
