#!/usr/bin/env python3

import time
import csv

cases = [9,14,30,57,118,300]

rows = []

for case in cases:

    start = time.time()

    # Placeholder runtime simulation
    time.sleep(0.05)

    runtime = time.time() - start

    rows.append([case, runtime])

    print(f"case{case}: {runtime:.4f}s")

with open("results/csv/scaling_results.csv", "w", newline="") as f:

    writer = csv.writer(f)

    writer.writerow(["buses", "runtime_sec"])

    writer.writerows(rows)
