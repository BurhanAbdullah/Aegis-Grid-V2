#!/usr/bin/env python3

import pandas as pd

df = pd.read_csv("results/csv/monte_carlo_results.csv")

total = len(df)

consensus_rate = df["consensus"].mean()

mitigation_rate = df["mitigation"].mean()

print("\n=== MONTE CARLO ANALYSIS ===")
print(f"Trials            : {total}")
print(f"Consensus Rate    : {consensus_rate:.3f}")
print(f"Mitigation Rate   : {mitigation_rate:.3f}")

assert (df["consensus"] == df["mitigation"]).all()

print("Consistency check passed.")
