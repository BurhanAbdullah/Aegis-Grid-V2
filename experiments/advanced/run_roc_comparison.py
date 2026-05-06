#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    roc_curve,
    auc
)

df = pd.read_csv(
    "paper/data/final_dataset_labeled.csv"
)

y_true = df["y_true"]

systems = {

    "Physics":
        df["kalman_anomaly"].astype(int),

    "Communication":
        df["jitter_detected"].astype(int),

    "Sequential":
        df["cusum_alarm"].astype(int),

    "Consensus":
        df["consensus"].astype(int),

    "Fusion":
        df["y_pred"].astype(int)
}

auc_rows = []

plt.figure(figsize=(8,6))

for name, score in systems.items():

    fpr, tpr, _ = roc_curve(
        y_true,
        score
    )

    roc_auc = auc(fpr, tpr)

    auc_rows.append({
        "system": name,
        "auc": roc_auc
    })

    plt.plot(
        fpr,
        tpr,
        label=f"{name} AUC={roc_auc:.3f}"
    )

plt.plot([0,1],[0,1],'k--')

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("Cross-Layer ROC Comparison")
plt.legend()

plt.savefig(
    "paper/figures/advanced/roc_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

pd.DataFrame(auc_rows).to_csv(
    "paper/data/advanced/roc_comparison.csv",
    index=False
)

print(pd.DataFrame(auc_rows))
