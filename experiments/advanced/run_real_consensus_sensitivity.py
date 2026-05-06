#!/usr/bin/env python3

import pandas as pd

from sklearn.metrics import (
    precision_score,
    recall_score
)

df = pd.read_csv(
    "paper/data/final_dataset_labeled.csv"
)

y_true = df["attack_label"]

rows = []

# =====================================================
# TEST DIFFERENT QUORUMS
# =====================================================

for quorum in [1, 2, 3]:

    votes = (
        df["monitor_vote"] +
        df["protector_vote"] +
        df["auditor_vote"]
    )

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
