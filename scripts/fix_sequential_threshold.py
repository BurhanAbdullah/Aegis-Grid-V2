#!/usr/bin/env python3

import pandas as pd

INPUT = "paper/data/sequential_physics.csv"

df = pd.read_csv(INPUT)

# =====================================================
# COMPUTE ADAPTIVE THRESHOLD
# =====================================================

mu = df["theta_seq"].mean()
sigma = df["theta_seq"].std()

# -----------------------------------------------------
# PREVIOUS:
# threshold = mu + 2*sigma
#
# TOO STRICT -> 0% alarms
#
# NEW:
# moderate sensitivity
# -----------------------------------------------------

threshold = mu + (0.5 * sigma)

# =====================================================
# GENERATE SEQUENTIAL ALARMS
# =====================================================

df["physics_alarm_seq"] = (
    df["theta_seq"] > threshold
).astype(int)

# =====================================================
# SAVE UPDATED DATASET
# =====================================================

df.to_csv(INPUT, index=False)

# =====================================================
# EXPORT THRESHOLD INFO
# =====================================================

with open(
    "paper/tables/sequential_threshold.txt",
    "w"
) as f:

    f.write(f"mean={mu:.4f}\n")
    f.write(f"std={sigma:.4f}\n")
    f.write(f"threshold={threshold:.4f}\n")

# =====================================================
# REPORT
# =====================================================

rate = df["physics_alarm_seq"].mean()

print("\n=== SEQUENTIAL PHYSICS CALIBRATION ===")
print(f"mean       : {mu:.4f}")
print(f"std        : {sigma:.4f}")
print(f"threshold  : {threshold:.4f}")
print(f"alarm_rate : {rate:.4f}")

print("\nSample rows:")
print(df[
    [
        "theta_seq",
        "physics_alarm_seq"
    ]
].head())

print("\n[OK] Sequential threshold updated.")
