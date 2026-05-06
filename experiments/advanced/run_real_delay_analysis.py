#!/usr/bin/env python3

import pandas as pd

df = pd.read_csv(
    "paper/data/final_dataset_labeled.csv"
)

# =====================================================
# REQUIRE scan index column
# =====================================================

if "scan_id" not in df.columns:

    df["scan_id"] = range(len(df))

# =====================================================
# DETECTION DELAY
# =====================================================

rows = []

for attack_name in df["attack"].unique():

    sub = df[
        df["attack"] == attack_name
    ]

    attack_start = sub["scan_id"].min()

    detected = sub[
        sub["prediction_label"] == 1
    ]

    if len(detected) > 0:

        first_detect = detected[
            "scan_id"
        ].min()

        delay = (
            first_detect -
            attack_start
        )

    else:

        delay = -1

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
