#!/usr/bin/env python3
"""
Authoritative Physical Experiment Runner for XMON-Grid Phase 3
File: scripts/run_authoritative_experiment.py

Executes the physical experiment pipeline using canonical models in core/xmon_model.py.
Outputs complete CSV dataset, metrics, tables, figures, independent verification, and SHA256SUMS.txt
into isolated directory: results/tsg_run_002/
"""

import sys, os, csv, json, hashlib, time, platform
sys.path.insert(0, os.path.abspath("."))

import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt

from scipy.stats import chi2
from sklearn.metrics import (
    confusion_matrix, accuracy_score, precision_score,
    recall_score, f1_score, roc_curve, auc, precision_recall_curve
)

from core.xmon_model import XMONGridModel, NISDetector
from core.data_pipeline import generate_physical_dataset

DEFAULT_OUTPUT_DIR = "results/tsg_run_003"
CASES = ["case9", "case14", "case30", "case118"]
SCENARIOS = ["baseline", "branch_outage", "fdia", "stealth_drift"]
SEED = 42

def create_directory_structure(target_dir):
    for sub in ["raw", "metrics", "tables", "figures"]:
        os.makedirs(os.path.join(target_dir, sub), exist_ok=True)

def run_experiment(seed=SEED, target_dir=None):
    if target_dir is None:
        target_dir = DEFAULT_OUTPUT_DIR
    print("\n==========================================================")
    print("RUNNING AUTHORITATIVE PHYSICAL EXPERIMENT (PHASE 3)")
    print(f"Target Output Directory : {target_dir}")
    print(f"Random Seed             : {seed}")
    print("==========================================================\n")
    
    create_directory_structure(target_dir)
    
    all_raw_rows = []
    all_detector_rows = []
    all_seq_rows = []
    calibration_records = []
    
    nis_calibration_samples = {c: [] for c in CASES}
    
    # 1. Loop through each IEEE test case
    for case_name in CASES:
        print(f"--- Processing Case: {case_name} ---")
        model = XMONGridModel(case_name=case_name)
        data = generate_physical_dataset(
            case_name=case_name,
            num_calibration=200,
            num_validation=100,
            num_test_per_scenario=60,
            seed=seed
        )
        
        # A. Calibrate model strictly on BENIGN calibration data
        print(f"  [1/3] Calibrating detectors on {len(data['calibration']['z'])} benign samples...")
        model.calibrate_benign(data["calibration"]["z"], data["calibration"]["iat"])
        
        calib_rec = {
            "case": case_name,
            "nis_threshold": model.nis_detector.threshold,
            "cusum_baseline_mean": model.cusum_detector.baseline_mean,
            "cusum_baseline_std": model.cusum_detector.baseline_std,
            "cusum_threshold": model.cusum_detector.threshold,
            "jitter_mu_T": model.jitter_detector.mu_T,
            "jitter_sigma_T": model.jitter_detector.sigma_T,
            "seq_threshold": model.sequential_accumulator.threshold,
            "tau_comp": round(model.tau_comp, 6)
        }
        calibration_records.append(calib_rec)
        
        # Reset model state after calibration
        model.reset()
            
        # B. Run Untouched Test Set Evaluation
        print(f"  [2/3] Evaluating on {len(data['test']['z'])} untouched test samples...")
        test_z = data["test"]["z"]
        test_iat = data["test"]["iat"]
        test_labels = data["test"]["labels"]
        test_meta = data["test"]["metadata"]
        
        current_scenario = None
        for idx in range(len(test_z)):
            z_meas = test_z[idx]
            dt_val = test_iat[idx]
            y_true = test_labels[idx]
            meta = test_meta[idx]
            
            # Reset stateful detectors and estimator at the start of every independent scenario
            if meta["scenario"] != current_scenario:
                current_scenario = meta["scenario"]
                model.reset()
            
            # Step canonical model
            step_res = model.step(z_meas, dt_val)
            
            sample_id = f"{case_name}_{meta['scenario']}_{meta['sample_idx']:03d}"
            
            if y_true == 0:
                nis_calibration_samples[case_name].append(step_res["nis"])
                
            # Raw dataset record
            raw_row = {
                "sample_id": sample_id,
                "case": case_name,
                "scenario": meta["scenario"],
                "severity_tier": meta.get("severity_tier", "Tier 0 (Benign)"),
                "attack_magnitude": meta.get("attack_magnitude", 0.0),
                "snr_estimate": meta.get("snr_estimate", 0.0),
                "sample_idx": meta["sample_idx"],
                "split": "test",
                "attack_label": y_true,
                "delta_t": round(dt_val, 6),
                "residual_norm": round(float(step_res["nis"]), 6),
            }
            all_raw_rows.append(raw_row)
            
            # Complete detector output record
            det_row = {
                "sample_id": sample_id,
                "case": case_name,
                "scenario": meta["scenario"],
                "severity_tier": meta.get("severity_tier", "Tier 0 (Benign)"),
                "attack_magnitude": meta.get("attack_magnitude", 0.0),
                "snr_estimate": meta.get("snr_estimate", 0.0),
                "sample_idx": meta["sample_idx"],
                "split": "test",
                "y_true": y_true,
                "nis": round(step_res["nis"], 4),
                "nis_threshold": round(step_res["nis_threshold"], 4),
                "a_nis": step_res["a_nis"],
                "cusum_g": round(step_res["cusum_g"], 4),
                "cusum_threshold": round(step_res["cusum_threshold"], 4),
                "a_cusum": step_res["a_cusum"],
                "a_cusum_inst": step_res["a_cusum_inst"],
                "jitter_z": round(step_res["jitter_z"], 4),
                "jitter_bar": round(step_res["jitter_bar"], 4),
                "a_jitter": step_res["a_jitter"],
                "s_comp": round(step_res["s_comp"], 6),
                "tau_comp": step_res["tau_comp"],
                "theta_seq": round(step_res["theta_seq"], 6),
                "theta_threshold": round(step_res["theta_threshold"], 6),
                "a_seq": step_res["a_seq"],
                "votes": step_res["votes"],
                "d_k2": step_res["d_k2"],
                "d_k1": step_res["d_k1"],
                "S_cond": round(step_res["S_cond"], 2)
            }
            all_detector_rows.append(det_row)
            
            # Sequential state trace
            seq_row = {
                "sample_id": sample_id,
                "case": case_name,
                "scenario": meta["scenario"],
                "y_true": y_true,
                "s_comp": round(step_res["s_comp"], 6),
                "theta_seq": round(step_res["theta_seq"], 6),
                "a_seq": step_res["a_seq"]
            }
            all_seq_rows.append(seq_row)
            
    print("  [3/3] Saving raw test data and detector trace CSVs...")
    
    # Save raw test dataset
    raw_csv = os.path.join(target_dir, "raw", "full_test_dataset.csv")
    with open(raw_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=all_raw_rows[0].keys())
        w.writeheader(); w.writerows(all_raw_rows)
        
    # Save detector outputs CSV
    det_csv = os.path.join(target_dir, "metrics", "detector_outputs.csv")
    with open(det_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=all_detector_rows[0].keys())
        w.writeheader(); w.writerows(all_detector_rows)
        
    # Save sequential states CSV
    seq_csv = os.path.join(target_dir, "metrics", "sequential_states.csv")
    with open(seq_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=all_seq_rows[0].keys())
        w.writeheader(); w.writerows(all_seq_rows)
        
    # Save threshold calibration table
    cal_csv = os.path.join(target_dir, "tables", "threshold_calibration.csv")
    with open(cal_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=calibration_records[0].keys())
        w.writeheader(); w.writerows(calibration_records)
        
    return all_detector_rows, nis_calibration_samples

# =====================================================================
# 2. Performance Metrics Calculation
# =====================================================================

def calculate_metrics(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    bal_acc = (rec + spec) / 2.0
    
    return {
        "TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp),
        "Accuracy": round(acc, 4), "Precision": round(prec, 4),
        "Recall": round(rec, 4), "F1": round(f1, 4),
        "FPR": round(fpr, 4), "Specificity": round(spec, 4),
        "Balanced_Accuracy": round(bal_acc, 4)
    }

def generate_tables(detector_rows, target_dir=None):
    if target_dir is None:
        target_dir = DEFAULT_OUTPUT_DIR
    y_true = np.array([r["y_true"] for r in detector_rows])
    
    # 1. Main Results (K=2 vs K=1 vs Standalones)
    detectors = [
        ("Quorum (K=2, Strict Majority)", [r["d_k2"] for r in detector_rows]),
        ("Quorum (K=1, Sensitivity Mode)", [r["d_k1"] for r in detector_rows]),
        ("NIS Standalone", [r["a_nis"] for r in detector_rows]),
        ("CUSUM Standalone", [r["a_cusum"] for r in detector_rows]),
        ("Jitter Standalone", [r["a_jitter"] for r in detector_rows]),
        ("Sequential Accumulator", [r["a_seq"] for r in detector_rows]),
    ]
    
    main_rows = []
    for name, pred in detectors:
        m = calculate_metrics(y_true, pred)
        m["Detector"] = name
        main_rows.append(m)
        
    main_csv = os.path.join(target_dir, "tables", "main_results.csv")
    with open(main_csv, "w", newline="") as f:
        fieldnames = ["Detector", "TN", "FP", "FN", "TP", "Accuracy", "Precision", "Recall", "F1", "FPR", "Specificity", "Balanced_Accuracy"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader(); w.writerows(main_rows)
        
    # 2. Confusion Matrices for K=2 and K=1
    for k_val, col in [(2, "d_k2"), (1, "d_k1")]:
        cm = confusion_matrix(y_true, [r[col] for r in detector_rows])
        cm_df = [
            {"Actual": "Normal (0)", "Predicted_Normal": cm[0,0], "Predicted_Attack": cm[0,1]},
            {"Actual": "Attack (1)", "Predicted_Normal": cm[1,0], "Predicted_Attack": cm[1,1]},
        ]
        with open(os.path.join(target_dir, "tables", f"confusion_matrix_k{k_val}.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["Actual", "Predicted_Normal", "Predicted_Attack"])
            w.writeheader(); w.writerows(cm_df)
            
    # 3. Case-wise and Attack-wise breakdown
    case_rows = []
    for c in CASES:
        c_rows = [r for r in detector_rows if r["case"] == c]
        c_true = [r["y_true"] for r in c_rows]
        for sc in SCENARIOS:
            sc_rows = [r for r in c_rows if r["scenario"] == sc]
            if sc_rows:
                sc_true = [r["y_true"] for r in sc_rows]
                sc_pred_k2 = [r["d_k2"] for r in sc_rows]
                m_k2 = calculate_metrics(sc_true, sc_pred_k2)
                case_rows.append({
                    "case": c, "scenario": sc, "num_samples": len(sc_rows),
                    "Precision": m_k2["Precision"], "Recall": m_k2["Recall"],
                    "F1": m_k2["F1"], "FPR": m_k2["FPR"]
                })
                
    with open(os.path.join(target_dir, "tables", "case_wise_results.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["case", "scenario", "num_samples", "Precision", "Recall", "F1", "FPR"])
        w.writeheader(); w.writerows(case_rows)

    # 4. ROC Curve Data (using Continuous Threat Score ONLY)
    scores = np.array([r["s_comp"] for r in detector_rows])
    fpr_arr, tpr_arr, thresholds = roc_curve(y_true, scores)
    roc_auc_val = float(auc(fpr_arr, tpr_arr))
    
    prec_arr, rec_arr, _ = precision_recall_curve(y_true, scores)
    pr_auc_val = float(auc(rec_arr, prec_arr))
    
    roc_rows = [{"fpr": round(f, 6), "tpr": round(t, 6), "threshold": round(th, 6)} for f, t, th in zip(fpr_arr, tpr_arr, thresholds)]
    with open(os.path.join(target_dir, "metrics", "roc_curve_data.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["fpr", "tpr", "threshold"])
        w.writeheader(); w.writerows(roc_rows)
        
    return roc_auc_val, pr_auc_val

# =====================================================================
# 3. Publication Figures Generation
# =====================================================================

def generate_figures(detector_rows, nis_samples, target_dir=None):
    if target_dir is None:
        target_dir = DEFAULT_OUTPUT_DIR
    print("  Generating publication figures...")
    y_true = np.array([r["y_true"] for r in detector_rows])
    scores = np.array([r["s_comp"] for r in detector_rows])
    
    fig_dir = os.path.join(target_dir, "figures")
    
    # Figure 1: Continuous Threat Score ROC Curve
    fpr, tpr, _ = roc_curve(y_true, scores)
    roc_auc_val = auc(fpr, tpr)
    
    plt.figure(figsize=(6, 5), dpi=300)
    plt.plot(fpr, tpr, color="#1f77b4", lw=2, label=f"Continuous Composite Score (AUC = {roc_auc_val:.4f})")
    plt.plot([0, 1], [0, 1], color="grey", linestyle="--", lw=1)
    plt.xlabel("False Positive Rate", fontsize=11)
    plt.ylabel("True Positive Rate", fontsize=11)
    plt.title("XMON-Grid ROC Curve (Pure Continuous Score)", fontsize=12, fontweight="bold")
    plt.legend(loc="lower right")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig1_roc_curve.png"))
    plt.close()
    
    # Figure 2: Precision-Recall Curve
    prec, rec, _ = precision_recall_curve(y_true, scores)
    pr_auc_val = auc(rec, prec)
    
    plt.figure(figsize=(6, 5), dpi=300)
    plt.plot(rec, prec, color="#2ca02c", lw=2, label=f"PR Curve (PR-AUC = {pr_auc_val:.4f})")
    plt.xlabel("Recall", fontsize=11)
    plt.ylabel("Precision", fontsize=11)
    plt.title("XMON-Grid Precision-Recall Curve", fontsize=12, fontweight="bold")
    plt.legend(loc="lower left")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig2_pr_curve.png"))
    plt.close()
    
    # Figure 3: Detector Comparison (K=2 vs K=1 vs Standalones)
    det_names = ["K=2 Quorum", "K=1 Quorum", "NIS", "CUSUM", "Jitter", "Sequential"]
    preds = [
        [r["d_k2"] for r in detector_rows],
        [r["d_k1"] for r in detector_rows],
        [r["a_nis"] for r in detector_rows],
        [r["a_cusum"] for r in detector_rows],
        [r["a_jitter"] for r in detector_rows],
        [r["a_seq"] for r in detector_rows],
    ]
    f1_scores = [f1_score(y_true, p, zero_division=0) for p in preds]
    rec_scores = [recall_score(y_true, p, zero_division=0) for p in preds]
    prec_scores = [precision_score(y_true, p, zero_division=0) for p in preds]
    
    x = np.arange(len(det_names))
    width = 0.25
    
    plt.figure(figsize=(9, 5), dpi=300)
    plt.bar(x - width, prec_scores, width, label="Precision", color="#1f77b4")
    plt.bar(x, rec_scores, width, label="Recall", color="#ff7f0e")
    plt.bar(x + width, f1_scores, width, label="F1-Score", color="#2ca02c")
    plt.xticks(x, det_names, rotation=15, fontsize=10)
    plt.ylabel("Score", fontsize=11)
    plt.ylim(0, 1.1)
    plt.title("XMON-Grid Detector Performance Comparison", fontsize=12, fontweight="bold")
    plt.legend(loc="lower right")
    plt.grid(axis="y", linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig3_detector_comparison.png"))
    plt.close()
    
    # Figure 4: Detector Agreement Heatmap
    det_matrix = np.array([
        [r["a_nis"] for r in detector_rows],
        [r["a_cusum"] for r in detector_rows],
        [r["a_jitter"] for r in detector_rows],
    ])
    corr_matrix = np.corrcoef(det_matrix)
    
    plt.figure(figsize=(6, 5), dpi=300)
    im = plt.imshow(corr_matrix, cmap="YlGnBu", vmin=0, vmax=1)
    plt.colorbar(im)
    plt.xticks(np.arange(3), ["NIS", "CUSUM", "Jitter"])
    plt.yticks(np.arange(3), ["NIS", "CUSUM", "Jitter"])
    for i in range(3):
        for j in range(3):
            plt.text(j, i, f"{corr_matrix[i, j]:.2f}", ha="center", va="center", color="black", fontweight="bold")
    plt.title("Detector Activation Agreement Matrix", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig4_agreement_heatmap.png"))
    plt.close()
    
    # Figure 5: NIS Nominal Distribution vs Theoretical Chi-Square Reference (Case9)
    nis_c9 = np.array(nis_samples["case9"])
    m_c9 = 27
    x_grid = np.linspace(0, 70, 200)
    pdf_chi2 = chi2.pdf(x_grid, df=m_c9)
    
    plt.figure(figsize=(7, 5), dpi=300)
    plt.hist(nis_c9, bins=30, density=True, alpha=0.6, color="#1f77b4", edgecolor="black", label="Empirical Benign NIS (case9)")
    plt.plot(x_grid, pdf_chi2, "r-", lw=2, label=f"Theoretical Chi-Square pdf (df={m_c9})")
    plt.axvline(x=chi2.ppf(0.99, df=m_c9), color="black", linestyle="--", label="Threshold gamma_NIS (99%)")
    plt.xlabel("NIS Value", fontsize=11)
    plt.ylabel("Probability Density", fontsize=11)
    plt.title("NIS Distribution vs Theoretical Chi-Square Reference", fontsize=12, fontweight="bold")
    plt.legend()
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig5_nis_distribution.png"))
    plt.close()
    
    # Figure 6: Case-wise F1 Comparison
    case_f1s = []
    for c in CASES:
        c_rows = [r for r in detector_rows if r["case"] == c]
        c_true = [r["y_true"] for r in c_rows]
        c_pred = [r["d_k2"] for r in c_rows]
        case_f1s.append(f1_score(c_true, c_pred, zero_division=0))
        
    plt.figure(figsize=(7, 5), dpi=300)
    plt.bar(CASES, case_f1s, color="#9467bd", width=0.5, edgecolor="black")
    plt.ylabel("K=2 F1-Score", fontsize=11)
    plt.ylim(0, 1.1)
    for i, v in enumerate(case_f1s):
        plt.text(i, v + 0.02, f"{v:.4f}", ha="center", fontweight="bold")
    plt.title("Case-Wise Performance Comparison (K=2 Quorum)", fontsize=12, fontweight="bold")
    plt.grid(axis="y", linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(fig_dir, "fig6_casewise_f1.png"))
    plt.close()

# =====================================================================
# 4. Independent Verification & Reproducibility Check
# =====================================================================

def independent_verification(det_csv_path):
    print("\n--- INDEPENDENT METRIC VERIFICATION ---")
    with open(det_csv_path, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    y_true = np.array([int(r["y_true"]) for r in rows])
    y_pred_k2 = np.array([int(r["d_k2"]) for r in rows])
    
    m = calculate_metrics(y_true, y_pred_k2)
    print("  Independent Verification Metrics (K=2 Quorum):")
    print(f"    TN={m['TN']}, FP={m['FP']}, FN={m['FN']}, TP={m['TP']}")
    print(f"    Accuracy={m['Accuracy']}, Precision={m['Precision']}, Recall={m['Recall']}, F1={m['F1']}")
    return m

def generate_sha256sums(target_dir=DEFAULT_OUTPUT_DIR):
    print("\n--- GENERATING CRYPTOGRAPHIC FREEZE (SHA256SUMS.txt) ---")
    sha_lines = []
    for root, _, files in os.walk(target_dir):
        for file in sorted(files):
            if file == "SHA256SUMS.txt":
                continue
            path = os.path.join(root, file)
            hasher = hashlib.sha256()
            with open(path, "rb") as f:
                hasher.update(f.read())
            rel_path = os.path.relpath(path, target_dir)
            sha_lines.append(f"{hasher.hexdigest()}  {rel_path}")
            
    sha_path = os.path.join(target_dir, "SHA256SUMS.txt")
    with open(sha_path, "w") as f:
        f.write("\n".join(sha_lines) + "\n")
    print(f"  Saved SHA256SUMS.txt with {len(sha_lines)} artifact signatures.")

if __name__ == "__main__":
    target_out_dir = sys.argv[1] if len(sys.argv) > 1 else "results/tsg_run_003"
    det_rows, nis_samples = run_experiment(seed=SEED, target_dir=target_out_dir)
    roc_auc_val, pr_auc_val = generate_tables(det_rows, target_dir=target_out_dir)
    generate_figures(det_rows, nis_samples, target_dir=target_out_dir)
    indep_m = independent_verification(os.path.join(target_out_dir, "metrics", "detector_outputs.csv"))
    generate_sha256sums(target_dir=target_out_dir)
    
    print("\n==========================================================")
    print("AUTHORITATIVE PHYSICAL EXPERIMENT EXECUTION COMPLETE")
    print(f"ROC AUC = {roc_auc_val:.4f} | PR-AUC = {pr_auc_val:.4f}")
    print(f"K=2 F1  = {indep_m['F1']:.4f} | K=2 Recall = {indep_m['Recall']:.4f}")
    print("==========================================================\n")
