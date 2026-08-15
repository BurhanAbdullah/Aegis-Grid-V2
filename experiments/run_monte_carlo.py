#!/usr/bin/env python3
# NOTE: Legacy/non-authoritative demonstration script.
import random
import csv

from core.consensus import compute_consensus
from core.mitigation import trigger_mitigation

N = 100

rows = []

for seed in range(N):

    random.seed(seed)

    # Simulated detector activations
    v_p = random.randint(0,1)
    v_m = random.randint(0,1)
    v_a = random.randint(0,1)

    consensus = compute_consensus(v_p, v_m, v_a)

    mitigation = trigger_mitigation(consensus)

    rows.append([
        seed,
        v_p,
        v_m,
        v_a,
        consensus,
        int(mitigation)
    ])

with open("results/csv/monte_carlo_results.csv", "w", newline="") as f:

    writer = csv.writer(f)

    writer.writerow([
        "seed",
        "v_p",
        "v_m",
        "v_a",
        "consensus",
        "mitigation"
    ])

    writer.writerows(rows)

print("Monte Carlo experiment complete.")
