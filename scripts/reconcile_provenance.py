#!/usr/bin/env python3
"""
Phase 3H — Authoritative Sample-Count and Provenance Reconciliation Script
File: scripts/reconcile_provenance.py

Performs deep read-only inspection of:
1. Line/row counts of all CSV files in results/tsg_run_002/
2. Sample counts by case, scenario, severity_tier in detector_outputs.csv and full_test_dataset.csv
3. Source code parameters in core/data_pipeline.py, scripts/run_authoritative_experiment.py, and scripts/run_comparative_ablation_analysis.py
4. Cryptographic signatures in results/tsg_run_002/SHA256SUMS.txt and run_metadata.txt
5. Confusion matrices recalculated directly from actual detector_outputs.csv rows
"""

import sys, os, csv, hashlib
import numpy as np

RESULTS_DIR = "results/tsg_run_002"

def reconcile():
    print("\n==========================================================")
    print("PHASE 3H — PROVENANCE & SAMPLE COUNT RECONCILIATION")
    print("==========================================================\n")
    
    # 1. Exact Row Counts of all CSV files in results/tsg_run_002/
    print("1. EXACT CSV FILE ROW COUNTS IN results/tsg_run_002/:")
    print("-" * 65)
    for root, _, files in os.walk(RESULTS_DIR):
        for f_name in sorted(files):
            if f_name.endswith(".csv"):
                f_path = os.path.join(root, f_name)
                with open(f_path, "r") as f:
                    r = csv.reader(f)
                    header = next(r, None)
                    data_rows = list(r)
                rel_path = os.path.relpath(f_path, RESULTS_DIR)
                print(f"  {rel_path:42s} : Header + {len(data_rows):5d} data rows")
                
    # 2. Composition of detector_outputs.csv
    det_path = os.path.join(RESULTS_DIR, "metrics", "detector_outputs.csv")
    with open(det_path, "r") as f:
        det_rows = list(csv.DictReader(f))
        
    print(f"\n2. DETECTOR_OUTPUTS.CSV DETAILED COMPOSITION:")
    print(f"   Total Rows: {len(det_rows)}")
    
    # Case breakdown
    cases = {}
    scenarios = {}
    tiers = {}
    case_scenarios = {}
    
    for r in det_rows:
        c = r["case"]
        sc = r["scenario"]
        t = r.get("severity_tier", "Unknown")
        
        cases[c] = cases.get(c, 0) + 1
        scenarios[sc] = scenarios.get(sc, 0) + 1
        tiers[t] = tiers.get(t, 0) + 1
        
        key = (c, sc, t)
        case_scenarios[key] = case_scenarios.get(key, 0) + 1
        
    print(f"\n   IEEE Case Breakdown:")
    for c, cnt in sorted(cases.items()):
        print(f"     - {c:10s} : {cnt} samples")
        
    print(f"\n   Scenario Breakdown:")
    for sc, cnt in sorted(scenarios.items()):
        print(f"     - {sc:15s} : {cnt} samples")
        
    print(f"\n   Severity Tier Breakdown:")
    for t, cnt in sorted(tiers.items()):
        print(f"     - {t:20s} : {cnt} samples")
        
    # 3. Source Code Provenance Investigation
    print("\n3. SOURCE CODE PROVENANCE INVESTIGATION:")
    # Check core/data_pipeline.py defaults
    with open("core/data_pipeline.py", "r") as f:
        dp_code = f.read()
    print("   core/data_pipeline.py parameter settings:")
    for line in dp_code.splitlines():
        if "num_test_per_scenario" in line or "test_scenarios" in line or "generate_physical_dataset(" in line:
            print(f"     {line.strip()}")
            
    # Check scripts/run_authoritative_experiment.py
    with open("scripts/run_authoritative_experiment.py", "r") as f:
        exp_code = f.read()
    print("\n   scripts/run_authoritative_experiment.py test configuration:")
    for line in exp_code.splitlines():
        if "num_test_per_scenario" in line or "NUM_TEST_PER_SCENARIO" in line or "generate_physical_dataset" in line:
            print(f"     {line.strip()}")
            
    # 4. Check run_metadata.txt
    meta_path = os.path.join(RESULTS_DIR, "run_metadata.txt")
    if os.path.exists(meta_path):
        print(f"\n4. CONTENTS OF results/tsg_run_002/run_metadata.txt:")
        with open(meta_path, "r") as f:
            print(f.read())
            
    # 5. Check SHA256SUMS.txt
    sha_path = os.path.join(RESULTS_DIR, "SHA256SUMS.txt")
    if os.path.exists(sha_path):
        print(f"\n5. SHA256SUMS.TXT ARTIFACT COUNT:")
        with open(sha_path, "r") as f:
            lines = f.readlines()
        print(f"   Signed Artifact Count: {len(lines)}")
        
    # 6. Recalculate Confusion Matrices directly from actual rows
    print("\n6. DIRECT CONFUSION MATRIX RECALCULATION (from 1,200 rows in detector_outputs.csv):")
    y_true = np.array([int(r["y_true"]) for r in det_rows])
    d_k2 = np.array([int(r["d_k2"]) for r in det_rows])
    d_k1 = np.array([int(r["d_k1"]) for r in det_rows])
    a_nis = np.array([int(r["a_nis"]) for r in det_rows])
    a_cusum = np.array([int(r["a_cusum"]) for r in det_rows])
    a_seq = np.array([int(r["a_seq"]) for r in det_rows])
    
    def cm_stats(yt, yp):
        tn = int(np.sum((yt == 0) & (yp == 0)))
        fp = int(np.sum((yt == 0) & (yp == 1)))
        fn = int(np.sum((yt == 1) & (yp == 0)))
        tp = int(np.sum((yt == 1) & (yp == 1)))
        acc = (tp + tn) / len(yt)
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        return f"TN={tn:3d}, FP={fp:3d}, FN={fn:3d}, TP={tp:3d} | Acc={acc:.4f}, Prec={prec:.4f}, Rec={rec:.4f}, F1={f1:.4f}, FPR={fpr:.4f}"
        
    print(f"   XMON-Grid K=2 : {cm_stats(y_true, d_k2)}")
    print(f"   XMON-Grid K=1 : {cm_stats(y_true, d_k1)}")
    print(f"   NIS Standalone: {cm_stats(y_true, a_nis)}")
    print(f"   CUSUM Standalone: {cm_stats(y_true, a_cusum)}")
    print(f"   Sequential-Only: {cm_stats(y_true, a_seq)}")

if __name__ == "__main__":
    reconcile()
