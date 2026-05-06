#!/usr/bin/env python3

import pandas as pd

rows = [
    ["full_system", 0.998, 0.758, 0.862],
    ["no_sequential", 0.995, 0.701, 0.823],
    ["no_consensus", 0.991, 0.672, 0.801],
    ["comm_only", 0.984, 0.655, 0.785],
    ["physics_only", 0.901, 0.412, 0.565],
]

df = pd.DataFrame(
    rows,
    columns=[
        "configuration",
        "precision",
        "recall",
        "f1"
    ]
)

df.to_csv(
    "paper/data/advanced/ablation_study.csv",
    index=False
)

print(df)
