#!/usr/bin/env python3

import pandas as pd
import numpy as np

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score
)

np.random.seed(42)

df = pd.read_csv(
    "paper/data/final_dataset_labeled.csv"
)

N = len(df)

precision_vals = []
recall_vals = []
f1_vals = []

for _ in range(1000):

    sample = df.sample(
        N,
        replace=True
    )

    y_true = sample["y_true"]
    y_pred = sample["y_pred"]

    precision_vals.append(
        precision_score(
            y_true,
            y_pred,
            zero_division=0
        )
    )

    recall_vals.append(
        recall_score(
            y_true,
            y_pred,
            zero_division=0
        )
    )

    f1_vals.append(
        f1_score(
            y_true,
            y_pred,
            zero_division=0
        )
    )

summary = pd.DataFrame([{

    "precision_mean":
        np.mean(precision_vals),

    "precision_ci_low":
        np.percentile(
            precision_vals,
            2.5
        ),

    "precision_ci_high":
        np.percentile(
            precision_vals,
            97.5
        ),

    "recall_mean":
        np.mean(recall_vals),

    "recall_ci_low":
        np.percentile(
            recall_vals,
            2.5
        ),

    "recall_ci_high":
        np.percentile(
            recall_vals,
            97.5
        ),

    "f1_mean":
        np.mean(f1_vals),

    "f1_ci_low":
        np.percentile(
            f1_vals,
            2.5
        ),

    "f1_ci_high":
        np.percentile(
            f1_vals,
            97.5
        )
}])

summary.to_csv(
    "paper/tables/advanced/confidence_intervals.csv",
    index=False
)

print(summary)
