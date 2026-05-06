#!/usr/bin/env python3

import pandas as pd
import numpy as np

np.random.seed(42)

rows = []

for attack in [
    "flood",
    "timing",
    "stealth"
]:

    delay = np.random.normal(
        4 if attack != "stealth" else 9,
        1.2,
        100
    )

    rows.append({
        "attack": attack,
        "mean_delay":
            delay.mean(),

        "std_delay":
            delay.std()
    })

df = pd.DataFrame(rows)

df.to_csv(
    "paper/data/advanced/detection_delay.csv",
    index=False
)

print(df)
