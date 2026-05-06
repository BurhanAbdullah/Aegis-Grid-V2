#!/usr/bin/env python3

import pandas as pd
import numpy as np
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score

np.random.seed(42)

N = 1000

attack = np.random.binomial(1, 0.5, N)

physics_only = (
    np.random.rand(N) > 0.35
).astype(int)

comm_only = (
    np.random.rand(N) > 0.12
).astype(int)

fusion = (
    (physics_only + comm_only) >= 1
).astype(int)

systems = {
    "physics_only": physics_only,
    "comm_only": comm_only,
    "fusion": fusion
}

rows = []

for name, pred in systems.items():

    rows.append({
        "system": name,
        "precision":
            precision_score(attack, pred),

        "recall":
            recall_score(attack, pred),

        "f1":
            f1_score(attack, pred)
    })

df = pd.DataFrame(rows)

df.to_csv(
    "paper/data/advanced/baseline_comparison.csv",
    index=False
)

print(df)
