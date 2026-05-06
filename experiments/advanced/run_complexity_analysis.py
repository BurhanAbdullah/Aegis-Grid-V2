#!/usr/bin/env python3

import pandas as pd

rows = [

    ["Kalman update", "O(n^2)"],
    ["CUSUM update", "O(1)"],
    ["Consensus voting", "O(N_agents)"],
    ["Threat fusion", "O(N_agents)"],
    ["Communication monitoring", "O(n)"],
    ["Sequential accumulation", "O(1)"]
]

df = pd.DataFrame(
    rows,
    columns=[
        "component",
        "complexity"
    ]
)

df.to_csv(
    "paper/tables/advanced/complexity_analysis.csv",
    index=False
)

print(df)
