#!/usr/bin/env python3

import pandas as pd

INPUT = "paper/data/sequential_physics.csv"

df = pd.read_csv(INPUT)

# =====================================================
# ADAPTIVE THRESHOLD
# =====================================================

mu = df["theta_seq"].mean()

sigma = df["theta_seq"].std()

threshold = mu + (2.0 * sigma)

df["physics_alarm_seq"] = (
    df["theta_seq"] > threshold
).astype(int)

# =====================================================
# SAVE UPDATED DATA
# =====================================================

OUTPUT = "paper/data/sequential_physics.csv"

df.to_csv(OUTPUT, index=False)

# =====================================================
# EXPORT THRESHOLD INFO
# =====================================================

with open(
    "paper/tables/sequential_threshold.txt",
    "w"
) as f:

    f.write(
        f"adaptive_threshold={threshold:.4f}\n"
    )

print(f"\nAdaptive threshold: {threshold:.4f}")

print(df[
    [
        "theta_seq",
        "physics_alarm_seq"
    ]
].head())

print(f"\n[OK] Updated -> {OUTPUT}")
