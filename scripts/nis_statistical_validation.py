#!/usr/bin/env python3
"""
NIS Statistical Validation Script for XMON-Grid
File: scripts/nis_statistical_validation.py

Evaluates empirical NIS distribution on benign calibration data vs theoretical Chi-Square reference chi2(df=m).
Reports theoretical mean (m), theoretical variance (2m), empirical mean, empirical variance,
quantiles, threshold gamma_NIS, and benign False Alarm Rate (FAR).
"""

import sys, os
sys.path.insert(0, os.path.abspath("."))

import numpy as np
from scipy.stats import chi2
from core.xmon_model import PowerSystemStateEstimator, NISDetector
from core.data_pipeline import generate_physical_dataset

CASES = ["case9", "case14", "case30", "case118"]

def validate_nis_statistics():
    print("==========================================================")
    print("NIS STATISTICAL VALIDATION REPORT (BENIGN NOMINAL TRAFFIC)")
    print("==========================================================")
    
    results = {}
    
    for case_name in CASES:
        estimator = PowerSystemStateEstimator(case_name=case_name)
        data = generate_physical_dataset(case_name=case_name, num_calibration=300, seed=42)
        
        # Warmup estimator over 10 steps so error covariance P reaches steady-state
        for z in data["calibration"]["z"][:10]:
            estimator.step(z)
            
        nis_vals = []
        for z in data["calibration"]["z"][10:]:
            res = estimator.step(z)
            nis_vals.append(res["nis"])
            
        nis_arr = np.array(nis_vals)
        m = estimator.meas_dim
        
        # Theoretical chi2(m) stats
        th_mean = float(m)
        th_var = float(2 * m)
        th_q50 = float(chi2.ppf(0.50, df=m))
        th_q95 = float(chi2.ppf(0.95, df=m))
        th_q99 = float(chi2.ppf(0.99, df=m))
        
        # Empirical stats
        emp_mean = float(np.mean(nis_arr))
        emp_var = float(np.var(nis_arr))
        emp_q50 = float(np.percentile(nis_arr, 50))
        emp_q95 = float(np.percentile(nis_arr, 95))
        emp_q99 = float(np.percentile(nis_arr, 99))
        
        detector = NISDetector(meas_dim=m, alpha=0.01)
        nis_threshold = detector.threshold
        
        # False alarm rate on benign calibration data
        alarms = [detector.update(val)[0] for val in nis_arr]
        far = float(np.mean(alarms))
        
        print(f"\n--- CASE: {case_name} (m = {m}) ---")
        print(f"Theoretical Mean  : {th_mean:.2f}  | Empirical Mean  : {emp_mean:.2f}")
        print(f"Theoretical Var   : {th_var:.2f}  | Empirical Var   : {emp_var:.2f}")
        print(f"Quantiles (50, 95, 99) Theo: ({th_q50:.1f}, {th_q95:.1f}, {th_q99:.1f})")
        print(f"Quantiles (50, 95, 99) Emp : ({emp_q50:.1f}, {emp_q95:.1f}, {emp_q99:.1f})")
        print(f"NIS Threshold (alpha=0.01)  : {nis_threshold:.2f}")
        print(f"Benign False Alarm Rate    : {far * 100:.2f}% (Expected ~ 1.00%)")
        
        results[case_name] = {
            "m": m,
            "th_mean": th_mean, "emp_mean": emp_mean,
            "th_var": th_var, "emp_var": emp_var,
            "th_q50": th_q50, "emp_q50": emp_q50,
            "th_q95": th_q95, "emp_q95": emp_q95,
            "th_q99": th_q99, "emp_q99": emp_q99,
            "threshold": nis_threshold,
            "far": far
        }
        
    return results

if __name__ == "__main__":
    validate_nis_statistics()
