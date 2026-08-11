#!/usr/bin/env python3
"""
Phase 3G Deep Forensic Audit Script
File: scripts/audit_phase3g_deep.py

Performs deep forensic inspection of core/xmon_model.py and results/tsg_run_002/
to answer all 13 Phase 3G scientific questions (A through M).
"""

import sys, os, csv
sys.path.insert(0, os.path.abspath("."))

import numpy as np

METRICS_CSV = "results/tsg_run_002/metrics/detector_outputs.csv"

def audit_deep():
    with open(METRICS_CSV, "r") as f:
        rows = list(csv.DictReader(f))
        
    print(f"Loaded {len(rows)} records from {METRICS_CSV}.\n")
    
    y_true = np.array([int(r["y_true"]) for r in rows])
    a_nis = np.array([int(r["a_nis"]) for r in rows])
    a_cusum = np.array([int(r["a_cusum"]) for r in rows])
    a_jitter = np.array([int(r["a_jitter"]) for r in rows])
    a_seq = np.array([int(r["a_seq"]) for r in rows])
    d_k2 = np.array([int(r["d_k2"]) for r in rows])
    d_k1 = np.array([int(r["d_k1"]) for r in rows])
    
    nis_vals = np.array([float(r["nis"]) for r in rows])
    nis_threshs = np.array([float(r["nis_threshold"]) for r in rows])
    
    # 1. Inspect a_nis logic
    benign_mask = (y_true == 0)
    benign_nis = nis_vals[benign_mask]
    benign_thresh = nis_threshs[benign_mask]
    benign_a_nis = a_nis[benign_mask]
    
    print("--- 1. NIS THRESHOLD & ALARM AUDIT ---")
    print(f"Benign Samples Count          : {len(benign_nis)}")
    print(f"Benign a_nis Alarm Count      : {np.sum(benign_a_nis)} / {len(benign_nis)} (FPR = {np.mean(benign_a_nis):.4f})")
    print(f"Sample Benign NIS Range       : [{np.min(benign_nis):.2f}, {np.max(benign_nis):.2f}]")
    print(f"Sample Benign Threshold Range : [{np.min(benign_thresh):.2f}, {np.max(benign_thresh):.2f}]")
    
    # Check why a_nis triggered
    num_exceed = np.sum(benign_nis > benign_thresh)
    print(f"Count of (nis > nis_threshold): {num_exceed} (Matches a_nis alarms: {num_exceed == np.sum(benign_a_nis)})")
    
    # 2. Inspect CUSUM logic
    benign_a_cusum = a_cusum[benign_mask]
    attack_a_cusum = a_cusum[~benign_mask]
    print("\n--- 2. CUSUM ALARM AUDIT ---")
    print(f"Benign a_cusum Alarms         : {np.sum(benign_a_cusum)} / {len(benign_nis)} (FPR = {np.mean(benign_a_cusum):.4f})")
    print(f"Attack a_cusum Alarms         : {np.sum(attack_a_cusum)} / {len(y_true)-len(benign_nis)} (Recall = {np.mean(attack_a_cusum):.4f})")
    
    # 3. Inspect Sequential Accumulator logic
    benign_a_seq = a_seq[benign_mask]
    attack_a_seq = a_seq[~benign_mask]
    print("\n--- 3. SEQUENTIAL ACCUMULATOR AUDIT ---")
    print(f"Benign a_seq Alarms           : {np.sum(benign_a_seq)} / {len(benign_nis)} (FPR = {np.mean(benign_a_seq):.4f})")
    print(f"Attack a_seq Alarms           : {np.sum(attack_a_seq)} / {len(y_true)-len(benign_nis)} (Recall = {np.mean(attack_a_seq):.4f})")
    
    # 4. Quorum Logic Audit
    print("\n--- 4. QUORUM LOGIC AUDIT ---")
    print(f"d_k2 (a_nis + a_cusum + a_jitter >= 2): FP = {np.sum(d_k2[benign_mask])}, TP = {np.sum(d_k2[~benign_mask])}")
    print(f"d_k1 (a_nis + a_cusum + a_jitter >= 1): FP = {np.sum(d_k1[benign_mask])}, TP = {np.sum(d_k1[~benign_mask])}")
    
    # 5. Check if Sequential Accumulator was included in Quorum
    quorum_with_seq_k2 = ((a_nis + a_cusum + a_jitter + a_seq) >= 2).astype(int)
    print(f"\nHypothetical Quorum WITH a_seq (>=2 votes out of 4):")
    print(f"  FP = {np.sum(quorum_with_seq_k2[benign_mask])}, TP = {np.sum(quorum_with_seq_k2[~benign_mask])}")

if __name__ == "__main__":
    audit_deep()
