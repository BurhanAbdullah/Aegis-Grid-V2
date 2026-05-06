#!/usr/bin/env python3

import pandas as pd

df = pd.read_csv(
    "paper/data/final_dataset_labeled.csv"
)

df["scan_id"] = range(len(df))

rows = []

for attack_name in df["attack"].unique():

    sub = df[
        df["attack"] == attack_name
    ]

    attack_start = sub["scan_id"].min()

    detected = sub[
        sub["y_pred"] == 1
    ]

    if len(detected) > 0:

        delay = (
            detected["scan_id"].min()
            - attack_start
        )

    else:

        delay = -1

    rows.append({

        "attack": attack_name,

        "detection_delay":
            int(delay)
    })

out = pd.DataFrame(rows)

out.to_csv(
    "paper/data/advanced/detection_delay.csv",
    index=False
)

print(out)
