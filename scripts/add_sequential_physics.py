#!/usr/bin/env python3

import pandas as pd

INPUT = "results/final_dataset.csv"
OUTPUT = "paper/data/sequential_physics.csv"

df = pd.read_csv(INPUT)

# Ensure NIS exists
if "nis" not in df.columns:
    raise ValueError("nis column missing")

# Sequential accumulator
theta = []

acc = 0.0

for nis in df["nis"]:

    # Simple accumulation dynamics
    acc = 0.9 * acc + float(nis)

    theta.append(acc)

df["theta_seq"] = theta

# Threshold crossing
df["physics_alarm_seq"] = (
    df["theta_seq"] > 3.0
).astype(int)

df.to_csv(OUTPUT, index=False)

print(df[
    ["nis", "theta_seq", "physics_alarm_seq"]
].head())

print(f"\n[OK] Saved -> {OUTPUT}")
