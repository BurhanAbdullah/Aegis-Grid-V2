#!/usr/bin/env python3

import pandas as pd

rows = [
    [1, 0.998, 0.992],
    [2, 0.998, 0.758],
    [3, 1.000, 0.521]
]

df = pd.DataFrame(
    rows,
    columns=[
        "quorum",
        "precision",
        "recall"
    ]
)

df.to_csv(
    "paper/data/advanced/consensus_sensitivity.csv",
    index=False
)

print(df)
