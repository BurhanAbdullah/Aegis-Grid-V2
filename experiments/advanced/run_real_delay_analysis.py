#!/usr/bin/env python3

import pandas as pd
import numpy as np

df = pd.read_csv(
    "paper/data/final_dataset_labeled.csv"
)

df["scan_id"] = range(len(df))

rows = []

for attack_name in df["attack"].unique():

    # ============================================
    # BASELINE HAS NO ATTACK
    # ============================================

    if attack_name == "baseline":

        rows.append({
            "attack": attack_name,
            "detection_delay": np.nan
        })

        continue

    # ============================================
    # REAL ATTACK SUBSET
    # ============================================

    sub = df[
        df["attack"] == attack_name
    ]

    attack_start = sub["scan_id"].min()

    detected = sub[
        sub["y_pred"] == 1
    ]

    # ============================================
    # DETECTION DELAY
    # ============================================

    if len(detected) > 0:

        delay = (
            detected["scan_id"].min()
            - attack_start
        )

    else:

        delay = np.nan

    rows.append({

        "attack": attack_name,

        "detection_delay":
            delay
    })

out = pd.DataFrame(rows)

out.to_csv(
    "paper/data/advanced/detection_delay.csv",
    index=False
)

print(out)
