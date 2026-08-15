#!/usr/bin/env python3
"""
Inspect NIS Alarm Rates per IEEE Case
File: scripts/audit_nis_cases.py
"""

import sys, os, csv
sys.path.insert(0, os.path.abspath("."))
import numpy as np

METRICS_CSV = "results/tsg_run_002/metrics/detector_outputs.csv"

def audit_cases():
    with open(METRICS_CSV, "r") as f:
        rows = list(csv.DictReader(f))
        
    for case in ["case9", "case14", "case30", "case118"]:
        c_benign = [r for r in rows if r["case"] == case and r["y_true"] == "0"]
        c_nis = [float(r["nis"]) for r in c_benign]
        c_thresh = [float(r["nis_threshold"]) for r in c_benign]
        c_anis = [int(r["a_nis"]) for r in c_benign]
        
        m = int(c_thresh[0])
        print(f"IEEE {case:8s} | Benign Samples: {len(c_benign)} | Thresh (df={m}): {c_thresh[0]:.2f} | Benign Mean NIS: {np.mean(c_nis):.2f} | Max NIS: {np.max(c_nis):.2f} | Alarms: {sum(c_anis)}/{len(c_benign)} ({sum(c_anis)/len(c_benign):.2%})")

if __name__ == "__main__":
    audit_cases()
