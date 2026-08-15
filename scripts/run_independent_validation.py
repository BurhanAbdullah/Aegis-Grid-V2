#!/usr/bin/env python3
"""Independent five-seed validation runner for the current XMON-Grid release."""
import sys, os, csv, json, hashlib, time
sys.path.insert(0, os.path.abspath("."))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import chi2
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score, roc_curve, auc, precision_recall_curve, matthews_corrcoef
from core.xmon_model import XMONGridModel
from core.data_pipeline import generate_physical_dataset

# Single source of truth for current scientific outputs.
TARGET_DIR = "results/authoritative_validation_20260815"
CASES = ["case9", "case14", "case30", "case118"]
SCENARIOS = ["baseline", "branch_outage", "fdia", "load_shift", "stealth_drift"]
PRIMARY_SEED = 2026
MULTI_SEEDS = [2026, 2027, 2028, 2029, 2030]

# The remainder of this module is intentionally unchanged in algorithmic scope:
# it calibrates only on benign data, evaluates untouched test data, computes the
# comparative baselines/ablations, runs all five seeds, and writes the complete
# detector trace and statistical tables into TARGET_DIR.

def create_dirs():
    for sub in ["raw", "metrics", "tables", "figures"]:
        os.makedirs(os.path.join(TARGET_DIR, sub), exist_ok=True)

def compute_all_metrics(y_true, y_pred, cont_scores=None):
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1]); tn, fp, fn, tp = cm.ravel()
    acc = accuracy_score(y_true, y_pred); prec = precision_score(y_true, y_pred, zero_division=0); rec = recall_score(y_true, y_pred, zero_division=0); f1 = f1_score(y_true, y_pred, zero_division=0)
    fpr = fp / (fp + tn) if fp + tn else 0.0; spec = tn / (tn + fp) if tn + fp else 0.0; bal_acc = (rec + spec) / 2.0; mcc = matthews_corrcoef(y_true, y_pred)
    roc_auc = pr_auc = 0.0
    if cont_scores is not None and len(np.unique(y_true)) > 1:
        fpr_arr, tpr_arr, _ = roc_curve(y_true, cont_scores); roc_auc = float(auc(fpr_arr, tpr_arr)); p_arr, r_arr, _ = precision_recall_curve(y_true, cont_scores); pr_auc = float(auc(r_arr, p_arr))
    return {"TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp), "Accuracy": float(acc), "Precision": float(prec), "Recall": float(rec), "F1": float(f1), "FPR": float(fpr), "Specificity": float(spec), "Balanced_Accuracy": float(bal_acc), "MCC": float(mcc), "ROC_AUC": float(roc_auc), "PR_AUC": float(pr_auc)}

def bootstrap_cis(y_true, y_pred, n_bootstraps=1000, seed=42):
    rng = np.random.RandomState(seed); n = len(y_true); vals = {k: [] for k in ("precision", "recall", "f1", "fpr", "mcc")}
    for _ in range(n_bootstraps):
        idxs = rng.choice(n, size=n, replace=True); m = compute_all_metrics(y_true[idxs], y_pred[idxs]); vals["precision"].append(m["Precision"]); vals["recall"].append(m["Recall"]); vals["f1"].append(m["F1"]); vals["fpr"].append(m["FPR"]); vals["mcc"].append(m["MCC"])
    def ci(v): return (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)))
    return {f"{k}_ci": ci(v) for k, v in vals.items()}

def run_experiment_seed(seed):
    all_det_rows = []; nis_samples = {c: [] for c in CASES}
    for case_name in CASES:
        model = XMONGridModel(case_name=case_name)
        data = generate_physical_dataset(case_name=case_name, num_calibration=200, num_validation=100, num_test_per_scenario=60, seed=seed)
        model.calibrate_benign(data["calibration"]["z"], data["calibration"]["iat"]); model.reset(); current_scenario = None
        for idx, z_meas in enumerate(data["test"]["z"]):
            dt_val = data["test"]["iat"][idx]; y_true = data["test"]["labels"][idx]; meta = data["test"]["metadata"][idx]
            if meta["scenario"] != current_scenario: current_scenario = meta["scenario"]; model.reset()
            step_res = model.step(z_meas, dt_val); sample_id = f"{case_name}_{meta['scenario']}_{meta['sample_idx']:03d}"
            if y_true == 0: nis_samples[case_name].append(step_res["nis"])
            all_det_rows.append({"seed": seed, "sample_id": sample_id, "case": case_name, "scenario": meta["scenario"], "severity_tier": meta.get("severity_tier", "Tier 0 (Benign)"), "attack_magnitude": meta.get("attack_magnitude", 0.0), "snr_estimate": meta.get("snr_estimate", 0.0), "sample_idx": meta["sample_idx"], "y_true": y_true, "nis": float(step_res["nis"]), "nis_threshold": float(step_res["nis_threshold"]), "a_nis": int(step_res["a_nis"]), "cusum_g": float(step_res["cusum_g"]), "cusum_threshold": float(step_res["cusum_threshold"]), "a_cusum": int(step_res["a_cusum"]), "a_cusum_inst": int(step_res["a_cusum_inst"]), "jitter_z": float(step_res["jitter_z"]), "jitter_bar": float(step_res["jitter_bar"]), "a_jitter": int(step_res["a_jitter"]), "s_comp": float(step_res["s_comp"]), "tau_comp": float(step_res["tau_comp"]), "theta_seq": float(step_res["theta_seq"]), "theta_threshold": float(step_res["theta_threshold"]), "a_seq": int(step_res["a_seq"]), "votes": int(step_res["votes"]), "d_k2": int(step_res["d_k2"]), "d_k1": int(step_res["d_k1"]), "S_cond": float(step_res["S_cond"])})
    return all_det_rows, nis_samples

def execute_independent_validation():
    create_dirs(); det_rows, nis_samples = run_experiment_seed(PRIMARY_SEED)
    with open(os.path.join(TARGET_DIR, "metrics", "detector_outputs.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=det_rows[0].keys()); w.writeheader(); w.writerows(det_rows)
    y_true = np.array([r["y_true"] for r in det_rows]); a_nis = np.array([r["a_nis"] for r in det_rows]); a_cusum = np.array([r["a_cusum"] for r in det_rows]); a_cusum_inst = np.array([r["a_cusum_inst"] for r in det_rows]); a_jitter = np.array([r["a_jitter"] for r in det_rows]); a_seq = np.array([r["a_seq"] for r in det_rows]); d_k2 = np.array([r["d_k2"] for r in det_rows]); d_k1 = np.array([r["d_k1"] for r in det_rows]); s_comp = np.array([r["s_comp"] for r in det_rows]); nis_cont = np.array([r["nis"] for r in det_rows]); cusum_cont = np.array([r["cusum_g"] for r in det_rows]); theta_cont = np.array([r["theta_seq"] for r in det_rows])
    methods = [("NIS Standalone", a_nis, nis_cont), ("CUSUM Standalone", a_cusum, cusum_cont), ("Jitter Standalone", a_jitter, None), ("NIS + CUSUM (OR)", (a_nis | a_cusum).astype(int), None), ("NIS + Jitter (OR)", (a_nis | a_jitter).astype(int), None), ("CUSUM + Jitter (OR)", (a_cusum | a_jitter).astype(int), None), ("Simple 3-Detector Majority Vote", ((a_nis + a_cusum + a_jitter) >= 2).astype(int), None), ("Sequential-Only Detector", a_seq, theta_cont), ("XMON-Grid K=2 (Strict Majority)", d_k2, s_comp), ("XMON-Grid K=1 (Sensitivity Mode)", d_k1, s_comp)]
    comp_results = []
    for name, pred, cont in methods:
        m = compute_all_metrics(y_true, pred, cont); ci = bootstrap_cis(y_true, pred); m["Method"] = name; m["Precision_CI"] = f"[{ci['precision_ci'][0]:.4f}, {ci['precision_ci'][1]:.4f}]"; m["Recall_CI"] = f"[{ci['recall_ci'][0]:.4f}, {ci['recall_ci'][1]:.4f}]"; m["F1_CI"] = f"[{ci['f1_ci'][0]:.4f}, {ci['f1_ci'][1]:.4f}]"; m["FPR_CI"] = f"[{ci['fpr_ci'][0]:.4f}, {ci['fpr_ci'][1]:.4f}]"; m["MCC_CI"] = f"[{ci['mcc_ci'][0]:.4f}, {ci['mcc_ci'][1]:.4f}]"; comp_results.append(m)
    with open(os.path.join(TARGET_DIR, "tables", "comparative_results.csv"), "w", newline="") as f:
        fields=["Method","TN","FP","FN","TP","Accuracy","Precision","Precision_CI","Recall","Recall_CI","F1","F1_CI","FPR","FPR_CI","Specificity","Balanced_Accuracy","MCC","MCC_CI","ROC_AUC","PR_AUC"]; w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(comp_results)
    tau_comp_val = float(det_rows[0]["tau_comp"])
    ablations=[("A. Full XMON-Grid (K=2 Quorum)",((a_nis+a_cusum+a_jitter)>=2).astype(int),s_comp),("B. XMON-Grid w/o NIS",((a_cusum+a_jitter)>=2).astype(int),None),("C. XMON-Grid w/o CUSUM",((a_nis+a_jitter)>=2).astype(int),None),("D. XMON-Grid w/o Jitter",((a_nis+a_cusum)>=2).astype(int),None),("E. XMON-Grid w/o Sequential Accumulation",((a_nis+a_cusum_inst+a_jitter)>=2).astype(int),s_comp),(f"F. XMON-Grid w/o Quorum Fusion (S_comp > {tau_comp_val:.4f})",(s_comp>tau_comp_val).astype(int),s_comp)]
    abl_results=[]
    for name,pred,cont in ablations:
        m=compute_all_metrics(y_true,pred,cont); ci=bootstrap_cis(y_true,pred); m["Configuration"]=name; m["F1_CI"]=f"[{ci['f1_ci'][0]:.4f}, {ci['f1_ci'][1]:.4f}]"; abl_results.append(m)
    with open(os.path.join(TARGET_DIR,"tables","ablation_results.csv"),"w",newline="") as f:
        fields=["Configuration","TN","FP","FN","TP","Accuracy","Precision","Recall","F1","F1_CI","FPR","Specificity","Balanced_Accuracy","MCC","ROC_AUC","PR_AUC"]; w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(abl_results)
    multi=[]
    for seed in MULTI_SEEDS:
        rows_s = det_rows if seed == PRIMARY_SEED else run_experiment_seed(seed)[0]; yt=np.array([r["y_true"] for r in rows_s]); pred=np.array([r["d_k2"] for r in rows_s]); m=compute_all_metrics(yt,pred); multi.append({"seed":seed,"Accuracy":m["Accuracy"],"Precision":m["Precision"],"Recall":m["Recall"],"F1":m["F1"],"FPR":m["FPR"],"MCC":m["MCC"]})
    with open(os.path.join(TARGET_DIR,"multi_seed_summary.csv"),"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["seed","Accuracy","Precision","Recall","F1","FPR","MCC"]); w.writeheader(); w.writerows(multi)
    print("INDEPENDENT FIVE-SEED VALIDATION COMPLETE")

if __name__ == "__main__":
    execute_independent_validation()
