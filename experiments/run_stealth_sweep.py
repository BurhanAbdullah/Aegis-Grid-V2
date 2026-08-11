#!/usr/bin/env python3
# NOTE: Legacy/non-authoritative demonstration script.
import csv

epsilons = [
    0.001,
    0.002,
    0.005,
    0.010,
    0.020
]

rows = []

for eps in epsilons:

    # Placeholder for REAL detector output
    detected = int(eps >= 0.005)

    rows.append([eps, detected])

    print(f"epsilon={eps:.3f} | detected={detected}")

with open("results/csv/stealth_sweep.csv", "w", newline="") as f:

    writer = csv.writer(f)

    writer.writerow([
        "epsilon",
        "detected"
    ])

    writer.writerows(rows)
