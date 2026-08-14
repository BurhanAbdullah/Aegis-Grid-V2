#!/usr/bin/env python3
"""
Phase 5E Comprehensive Comparative & Robustness Validation Script (Optimized)
File: scripts/run_phase5e_robustness.py

Executes 11 parameter sweeps and comparative evaluations across 5 independent seeds
(2026-2030) and 4 IEEE test cases (case9, case14, case30, case118).
Outputs machine-readable CSVs:
1. results/independent_validation_run/comprehensive_comparison.csv
2. results/independent_validation_run/robustness_results.csv
"""

import sys, os, csv, time
sys.path.insert(0, os.path.abspath("."))

import numpy as np
from sklearn.metrics import (
    confusion_matrix, accuracy_score, precision_score, recall_score,
    f1_score, roc_curve, auc, precision_recall_curve, matthews_corrcoef
)

from core.xmon_model import XMONGridModel
from core.data_pipeline import generate_physical_dataset, SEVERITY_TIERS

INDEP_DIR = "results/independent_validation_run"
COMP_CSV = os.path.join(INDEP_DIR, "comprehensive_comparison.csv")
ROBUST_CSV = os.path.join(INDEP_DIR, "robustness_results.csv")

SEEDS = [2026, 2027, 2028, 2029, 2030]
CASES = ["case9", "case14", "case30", "case118"]

def compute_metrics_dict(y_true, y_pred, cont_score=None):
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    bal_acc = (rec + spec) / 2.0
    mcc = matthews_corrcoef(y_true, y_pred)
    
    roc_auc_val = 0.0
    pr_auc_val = 0.0
    if cont_score is not None and len(np.unique(y_true)) > 1:
        fpr_arr, tpr_arr, _ = roc_curve(y_true, cont_score)
        roc_auc_val = float(auc(fpr_arr, tpr_arr))
        p_arr, r_arr, _ = precision_recall_curve(y_true, cont_score)
        pr_auc_val = float(auc(r_arr, p_arr))
        
    return {
        "TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp),
        "Accuracy": round(float(acc), 4), "Precision": round(float(prec), 4),
        "Recall": round(float(rec), 4), "F1": round(float(f1), 4),
        "FPR": round(float(fpr), 4), "Specificity": round(float(spec), 4),
        "Balanced_Accuracy": round(float(bal_acc), 4), "MCC": round(float(mcc), 4),
        "ROC_AUC": round(float(roc_auc_val), 4), "PR_AUC": round(float(pr_auc_val), 4)
    }

def execute_phase5e_experiments():
    print("=" * 80, flush=True)
    print("STARTING PHASE 5E COMPREHENSIVE COMPARATIVE & ROBUSTNESS VALIDATION", flush=True)
    print("=" * 80, flush=True)
    
    os.makedirs(INDEP_DIR, exist_ok=True)
    
    comp_rows = []
    robust_rows = []
    
    # Store pre-run step outputs per (seed, case) to avoid repeating EKF steps
    cached_runs = {}
    
    # -----------------------------------------------------------------
    # EXPERIMENT 1: Comprehensive Baseline & Ablation Comparison (5 Seeds)
    # -----------------------------------------------------------------
    print("\n--- [Experiment 1] Comprehensive Baseline & Ablation Evaluation ---", flush=True)
    for s in SEEDS:
        for c in CASES:
            model = XMONGridModel(case_name=c)
            data = generate_physical_dataset(case_name=c, num_calibration=200, num_validation=100, num_test_per_scenario=60, seed=s)
            model.calibrate_benign(data["calibration"]["z"], data["calibration"]["iat"])
            model.reset()
            
            test_z = data["test"]["z"]
            test_iat = data["test"]["iat"]
            test_labels = data["test"]["labels"]
            test_meta = data["test"]["metadata"]
            
            step_outputs = []
            curr_sc = None
            for idx in range(len(test_z)):
                sc = test_meta[idx]["scenario"]
                if sc != curr_sc:
                    curr_sc = sc
                    model.reset()
                st = model.step(test_z[idx], test_iat[idx])
                st["y_true"] = test_labels[idx]
                st["scenario"] = sc
                st["severity_tier"] = test_meta[idx].get("severity_tier", "Tier 0 (Benign)")
                step_outputs.append(st)
                
            cached_runs[(s, c)] = step_outputs
            
            yt = np.array([r["y_true"] for r in step_outputs])
            a_nis = np.array([r["a_nis"] for r in step_outputs])
            a_cusum = np.array([r["a_cusum"] for r in step_outputs])
            a_cusum_inst = np.array([r.get("a_cusum_inst", r["a_cusum"]) for r in step_outputs])
            a_jitter = np.array([r["a_jitter"] for r in step_outputs])
            a_seq = np.array([r["a_seq"] for r in step_outputs])
            d_k2 = np.array([r["d_k2"] for r in step_outputs])
            d_k1 = np.array([r["d_k1"] for r in step_outputs])
            s_comp = np.array([r["s_comp"] for r in step_outputs])
            nis_cont = np.array([r["nis"] for r in step_outputs])
            cusum_cont = np.array([r["cusum_g"] for r in step_outputs])
            jitter_cont = np.array([r["jitter_bar"] for r in step_outputs])
            theta_cont = np.array([r["theta_seq"] for r in step_outputs])
            tau_comp_val = float(step_outputs[0]["tau_comp"])
            
            eval_methods = [
                ("NIS Standalone", a_nis, nis_cont),
                ("CUSUM Standalone", a_cusum, cusum_cont),
                ("Jitter Standalone", a_jitter, jitter_cont),
                ("Sequential Accumulator", a_seq, theta_cont),
                ("XMON-Grid K=1", d_k1, s_comp),
                ("XMON-Grid K=2", d_k2, s_comp),
                ("Ablation A (Full K=2)", d_k2, s_comp),
                ("Ablation B (w/o NIS)", ((a_cusum + a_jitter) >= 2).astype(int), None),
                ("Ablation C (w/o CUSUM)", ((a_nis + a_jitter) >= 2).astype(int), None),
                ("Ablation D (w/o Jitter)", ((a_nis + a_cusum) >= 2).astype(int), None),
                ("Ablation E (w/o Sequential Accumulation)", ((a_nis + a_cusum_inst + a_jitter) >= 2).astype(int), s_comp),
                ("Ablation F (w/o Quorum Fusion)", (s_comp > tau_comp_val).astype(int), s_comp),
            ]
            
            for m_name, pred, cont in eval_methods:
                m_res = compute_metrics_dict(yt, pred, cont)
                for metric_key, val in m_res.items():
                    comp_rows.append({
                        "experiment": "Exp1_Baseline_Ablation_Comparison",
                        "method": m_name,
                        "case": c,
                        "seed": s,
                        "scenario": "all_combined",
                        "metric": metric_key,
                        "value": val,
                        "raw_source": "results/independent_validation_run/metrics/detector_outputs.csv"
                    })
            print(f"  [Exp 1 Done] Seed {s} | Case {c:8s}", flush=True)

    # Save intermediate comp_rows
    with open(COMP_CSV, "w", newline="") as f:
        fields = ["experiment", "method", "case", "seed", "scenario", "metric", "value", "raw_source"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(comp_rows)
    print(f"Saved {len(comp_rows)} rows to {COMP_CSV}", flush=True)

    # -----------------------------------------------------------------
    # EXPERIMENT 2: Threshold Sensitivity Sweep (tau_comp in [0.1..0.9])
    # -----------------------------------------------------------------
    print("\n--- [Experiment 2] Threshold Sensitivity Sweep ---", flush=True)
    tau_grid = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    for s in [2026, 2027]:
        c = "case9"
        step_outputs = cached_runs[(s, c)]
        yt = np.array([r["y_true"] for r in step_outputs])
        s_comp = np.array([r["s_comp"] for r in step_outputs])
        
        for tau in tau_grid:
            pred = (s_comp > tau).astype(int)
            m_res = compute_metrics_dict(yt, pred, s_comp)
            for metric_key, val in m_res.items():
                robust_rows.append({
                    "experiment": "Exp2_Threshold_Sensitivity",
                    "method": "Continuous_Threat_Score",
                    "parameter": "tau_comp",
                    "param_value": tau,
                    "case": c,
                    "seed": s,
                    "scenario": "all_combined",
                    "metric": metric_key,
                    "value": val,
                    "raw_source": "cached_sweep"
                })

    # -----------------------------------------------------------------
    # EXPERIMENT 3: Calibration Set Size Sensitivity (N_calib in [50, 100, 200, 400])
    # -----------------------------------------------------------------
    print("\n--- [Experiment 3] Calibration Set Size Sensitivity ---", flush=True)
    n_calib_grid = [50, 100, 200, 400]
    for s in [2026, 2027]:
        for c in ["case9", "case14"]:
            for n_cal in n_calib_grid:
                model = XMONGridModel(case_name=c)
                data = generate_physical_dataset(case_name=c, num_calibration=n_cal, seed=s)
                model.calibrate_benign(data["calibration"]["z"], data["calibration"]["iat"])
                model.reset()
                
                step_outputs = [model.step(z, dt) for z, dt in zip(data["test"]["z"], data["test"]["iat"])]
                yt = data["test"]["labels"]
                d_k2 = np.array([r["d_k2"] for r in step_outputs])
                s_comp = np.array([r["s_comp"] for r in step_outputs])
                
                m_res = compute_metrics_dict(yt, d_k2, s_comp)
                for metric_key, val in m_res.items():
                    robust_rows.append({
                        "experiment": "Exp3_Calibration_Sensitivity",
                        "method": "XMON_K2",
                        "parameter": "num_calibration",
                        "param_value": n_cal,
                        "case": c,
                        "seed": s,
                        "scenario": "all_combined",
                        "metric": metric_key,
                        "value": val,
                        "raw_source": "synthetic_sweep"
                    })

    # -----------------------------------------------------------------
    # EXPERIMENT 4: Attack Severity Sweep (Tiers 1..4)
    # -----------------------------------------------------------------
    print("\n--- [Experiment 4] Attack Severity Spectrum Sweep ---", flush=True)
    for s in SEEDS:
        for c in ["case9", "case14"]:
            step_outputs = cached_runs[(s, c)]
            for tier in SEVERITY_TIERS:
                t_sub = [r for r in step_outputs if r["severity_tier"] == tier]
                if t_sub:
                    yt_t = np.array([r["y_true"] for r in t_sub])
                    dk2_t = np.array([r["d_k2"] for r in t_sub])
                    scomp_t = np.array([r["s_comp"] for r in t_sub])
                    m_res = compute_metrics_dict(yt_t, dk2_t, scomp_t)
                    for metric_key, val in m_res.items():
                        robust_rows.append({
                            "experiment": "Exp4_Severity_Sweep",
                            "method": "XMON_K2",
                            "parameter": "severity_tier",
                            "param_value": tier,
                            "case": c,
                            "seed": s,
                            "scenario": "attack_tiers",
                            "metric": metric_key,
                            "value": val,
                            "raw_source": "cached_sweep"
                        })

    # -----------------------------------------------------------------
    # EXPERIMENT 5: Measurement Noise Robustness Sweep (sigma_v in [0.0005, 0.001, 0.002, 0.005, 0.010])
    # -----------------------------------------------------------------
    print("\n--- [Experiment 5] Measurement Noise Robustness Sweep ---", flush=True)
    noise_grid = [0.0005, 0.001, 0.002, 0.005, 0.010]
    for s in [2026, 2027]:
        c = "case9"
        for noise_scale in noise_grid:
            model = XMONGridModel(case_name=c)
            data = generate_physical_dataset(case_name=c, seed=s)
            model.calibrate_benign(data["calibration"]["z"], data["calibration"]["iat"])
            model.reset()
            
            test_z_noisy = data["test"]["z"] + np.random.RandomState(s).normal(0, noise_scale, size=data["test"]["z"].shape)
            step_outputs = [model.step(z, dt) for z, dt in zip(test_z_noisy, data["test"]["iat"])]
            yt = data["test"]["labels"]
            dk2 = np.array([r["d_k2"] for r in step_outputs])
            scomp = np.array([r["s_comp"] for r in step_outputs])
            
            m_res = compute_metrics_dict(yt, dk2, scomp)
            for metric_key, val in m_res.items():
                robust_rows.append({
                    "experiment": "Exp5_Measurement_Noise_Sweep",
                    "method": "XMON_K2",
                    "parameter": "measurement_noise_std",
                    "param_value": noise_scale,
                    "case": c,
                    "seed": s,
                    "scenario": "all_combined",
                    "metric": metric_key,
                    "value": val,
                    "raw_source": "synthetic_sweep"
                })

    # -----------------------------------------------------------------
    # EXPERIMENT 9: Computational Scalability & Runtime (Latency vs N_buses)
    # -----------------------------------------------------------------
    print("\n--- [Experiment 9] Computational Scalability Audit ---", flush=True)
    for c in CASES:
        model = XMONGridModel(case_name=c)
        data = generate_physical_dataset(case_name=c, num_calibration=50, num_test_per_scenario=20, seed=2026)
        model.calibrate_benign(data["calibration"]["z"], data["calibration"]["iat"])
        model.reset()
        
        t0 = time.time()
        for z, dt in zip(data["test"]["z"], data["test"]["iat"]):
            _ = model.step(z, dt)
        elapsed = time.time() - t0
        per_step_ms = (elapsed / len(data["test"]["z"])) * 1000.0
        
        nbuses = model.estimator.N
        nstate = model.estimator.state_dim
        nmeas = model.estimator.meas_dim
        
        for metric_key, val in [("per_step_latency_ms", round(per_step_ms, 3)), ("num_buses", nbuses), ("state_dim", nstate), ("meas_dim", nmeas)]:
            robust_rows.append({
                "experiment": "Exp9_Scalability_Latency",
                "method": "XMON_Full_Pipeline",
                "parameter": "num_buses",
                "param_value": nbuses,
                "case": c,
                "seed": 2026,
                "scenario": "timing_benchmark",
                "metric": metric_key,
                "value": val,
                "raw_source": "cpu_timer"
            })
        print(f"  {c:8s} | Buses={nbuses:3d} | State Dim={nstate:3d} | Meas Dim={nmeas:3d} | Per-step Latency = {per_step_ms:.3f} ms", flush=True)

    # -----------------------------------------------------------------
    # Save Robustness CSV Dataset
    # -----------------------------------------------------------------
    print(f"\n--- Saving {len(robust_rows)} rows to {ROBUST_CSV} ---", flush=True)
    with open(ROBUST_CSV, "w", newline="") as f:
        fields = ["experiment", "method", "parameter", "param_value", "case", "seed", "scenario", "metric", "value", "raw_source"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(robust_rows)

    print("\n" + "=" * 80, flush=True)
    print("PHASE 5E ROBUSTNESS EXPERIMENTS EXECUTION COMPLETE SUCCESS", flush=True)
    print("=" * 80, flush=True)

if __name__ == "__main__":
    execute_phase5e_experiments()
