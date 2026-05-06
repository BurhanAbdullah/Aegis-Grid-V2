#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score
)

df = pd.read_csv(
    "paper/data/final_dataset_labeled.csv"
)

y_true = df["y_true"]

rows = []

thresholds = np.linspace(
    0,
    1,
    21
)

for th in thresholds:

    pred = (
        df["threat_score"] >= th
    ).astype(int)

    rows.append({

        "threshold": th,

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
    "paper/data/advanced/threshold_sweep.csv",
    index=False
)

plt.figure(figsize=(8,6))

plt.plot(
    out["threshold"],
    out["precision"],
    label="Precision"
)

plt.plot(
    out["threshold"],
    out["recall"],
    label="Recall"
)

plt.plot(
    out["threshold"],
    out["f1"],
    label="F1"
)

plt.xlabel("Threat Threshold")
plt.ylabel("Metric")
plt.title("Threshold Sensitivity Analysis")
plt.legend()

plt.savefig(
    "paper/figures/advanced/threshold_sweep.png",
    dpi=300,
    bbox_inches="tight"
)

print(out)
