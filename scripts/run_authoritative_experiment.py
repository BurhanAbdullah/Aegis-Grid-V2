#!/usr/bin/env python3
"""Authoritative XMON-Grid experiment using the canonical physical pipeline."""

import sys, os, csv, json, hashlib, time, platform
sys.path.insert(0, os.path.abspath("."))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import chi2
from sklearn.metrics import (confusion_matrix, accuracy_score, precision_score,
    recall_score, f1_score, roc_curve, auc, precision_recall_curve)

from core.xmon_model import XMONGridModel
from core.physical_data_pipeline import generate_physical_dataset

DEFAULT_OUTPUT_DIR = "results/real_validation_run"
CASES = ["case9", "case14", "case30", "case118"]
SCENARIOS = ["baseline", "branch_outage", "fdia", "load_shift", "stealth_drift"]
SEED = 42

# The remainder of this file is the original authoritative reporting pipeline.
# It consumes the physical dataset above and does not change detector logic.

def create_directory_structure(target_dir):
    for sub in ["raw", "metrics", "tables", "figures"]:
        os.makedirs(os.path.join(target_dir, sub), exist_ok=True)

def calculate_metrics(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1]); tn, fp, fn, tp = cm.ravel()
    acc = accuracy_score(y_true, y_pred); prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0); f1 = f1_score(y_true, y_pred, zero_division=0)
    fpr = fp / (fp + tn) if fp + tn else 0.0; spec = tn / (tn + fp) if tn + fp else 0.0
    return {"TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp), "Accuracy": round(acc, 4),
            "Precision": round(prec, 4), "Recall": round(rec, 4), "F1": round(f1, 4),
            "FPR": round(fpr, 4), "Specificity": round(spec, 4), "Balanced_Accuracy": round((rec + spec) / 2, 4)}

def run_experiment(seed=SEED, target_dir=DEFAULT_OUTPUT_DIR):
    create_directory_structure(target_dir)
    all_raw, all_det, all_seq, calibration_records = [], [], [], []
    nis_calibration_samples = {c: [] for c in CASES}
    for case_name in CASES:
        model = XMONGridModel(case_name=case_name)
        data = generate_physical_dataset(case_name, num_calibration=200, num_validation=100,
                                          num_test_per_scenario=60, seed=seed)
        model.calibrate_benign(data["calibration"]["z"], data["calibration"]["iat"])
        calibration_records.append({"case": case_name, "nis_threshold": model.nis_detector.threshold,
            "cusum_baseline_mean": model.cusum_detector.baseline_mean,
            "cusum_baseline_std": model.cusum_detector.baseline_std,
            "cusum_threshold": model.cusum_detector.threshold,
            "jitter_mu_T": model.jitter_detector.mu_T, "jitter_sigma_T": model.jitter_detector.sigma_T,
            "seq_threshold": model.sequential_accumulator.threshold, "tau_comp": round(model.tau_comp, 6)})
        model.reset(); current_scenario = None
        for idx, (z_meas, dt_val, y_true, meta) in enumerate(zip(data["test"]["z"], data["test"]["iat"],
                                                                  data["test"]["labels"], data["test"]["metadata"])):
            if meta["scenario"] != current_scenario:
                current_scenario = meta["scenario"]; model.reset()
            step = model.step(z_meas, dt_val)
            sample_id = f"{case_name}_{meta['scenario']}_{meta['sample_idx']:03d}"
            if y_true == 0: nis_calibration_samples[case_name].append(step["nis"])
            all_raw.append({"sample_id": sample_id, "case": case_name, "scenario": meta["scenario"],
                "severity_tier": meta.get("severity_tier", "Tier 0 (Benign)"),
                "attack_magnitude": meta.get("attack_magnitude", 0.0), "snr_estimate": meta.get("snr_estimate", 0.0),
                "sample_idx": meta["sample_idx"], "split": "test", "attack_label": int(y_true),
                "delta_t": round(float(dt_val), 6), "residual_norm": round(float(step["nis"]), 6),
                "attack_mode": meta.get("attack_mode", "")})
            all_det.append({"sample_id": sample_id, "case": case_name, "scenario": meta["scenario"],
                "severity_tier": meta.get("severity_tier", "Tier 0 (Benign)"),
                "attack_magnitude": meta.get("attack_magnitude", 0.0), "snr_estimate": meta.get("snr_estimate", 0.0),
                "sample_idx": meta["sample_idx"], "split": "test", "y_true": int(y_true),
                "nis": round(float(step["nis"]), 4), "nis_threshold": round(float(step["nis_threshold"]), 4),
                "a_nis": int(step["a_nis"]), "cusum_g": round(float(step["cusum_g"]), 4),
                "cusum_threshold": round(float(step["cusum_threshold"]), 4), "a_cusum": int(step["a_cusum"]),
                "a_cusum_inst": int(step["a_cusum_inst"]), "jitter_z": round(float(step["jitter_z"]), 4),
                "jitter_bar": round(float(step["jitter_bar"]), 4), "a_jitter": int(step["a_jitter"]),
                "s_comp": round(float(step["s_comp"]), 6), "tau_comp": float(step["tau_comp"]),
                "theta_seq": round(float(step["theta_seq"]), 6), "theta_threshold": round(float(step["theta_threshold"]), 6),
                "a_seq": int(step["a_seq"]), "votes": int(step["votes"]), "d_k2": int(step["d_k2"]),
                "d_k1": int(step["d_k1"]), "S_cond": round(float(step["S_cond"]), 2)})
            all_seq.append({"sample_id": sample_id, "case": case_name, "scenario": meta["scenario"],
                "y_true": int(y_true), "s_comp": round(float(step["s_comp"]), 6),
                "theta_seq": round(float(step["theta_seq"]), 6), "a_seq": int(step["a_seq"])})

    def write_csv(path, rows):
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    write_csv(os.path.join(target_dir, "raw", "full_test_dataset.csv"), all_raw)
    write_csv(os.path.join(target_dir, "metrics", "detector_outputs.csv"), all_det)
    write_csv(os.path.join(target_dir, "metrics", "sequential_states.csv"), all_seq)
    write_csv(os.path.join(target_dir, "tables", "threshold_calibration.csv"), calibration_records)
    return all_det, nis_calibration_samples

def generate_tables(rows, target_dir):
    y = np.array([r["y_true"] for r in rows])
    detectors = [("Quorum (K=2, Strict Majority)", "d_k2"), ("Quorum (K=1, Sensitivity Mode)", "d_k1"),
                 ("NIS Standalone", "a_nis"), ("CUSUM Standalone", "a_cusum"),
                 ("Jitter Standalone", "a_jitter"), ("Sequential Accumulator", "a_seq")]
    main = []
    for name, col in detectors:
        m = calculate_metrics(y, [r[col] for r in rows]); m["Detector"] = name; main.append(m)
    write_path = os.path.join(target_dir, "tables", "main_results.csv")
    with open(write_path, "w", newline="") as f:
        fields = ["Detector","TN","FP","FN","TP","Accuracy","Precision","Recall","F1","FPR","Specificity","Balanced_Accuracy"]
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(main)
    for k, col in [(2, "d_k2"), (1, "d_k1")]:
        cm = confusion_matrix(y, [r[col] for r in rows], labels=[0,1])
        with open(os.path.join(target_dir, "tables", f"confusion_matrix_k{k}.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["Actual","Predicted_Normal","Predicted_Attack"]); w.writeheader()
            w.writerows([{"Actual":"Normal (0)","Predicted_Normal":cm[0,0],"Predicted_Attack":cm[0,1]},
                         {"Actual":"Attack (1)","Predicted_Normal":cm[1,0],"Predicted_Attack":cm[1,1]}])
    scores = np.array([r["s_comp"] for r in rows]); fpr, tpr, thresholds = roc_curve(y, scores)
    roc_auc = float(auc(fpr, tpr)); prec, rec, _ = precision_recall_curve(y, scores); pr_auc = float(auc(rec, prec))
    write_path = os.path.join(target_dir, "metrics", "roc_curve_data.csv")
    with open(write_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["fpr","tpr","threshold"]); w.writeheader()
        w.writerows({"fpr":round(float(a),6),"tpr":round(float(b),6),"threshold":round(float(c),6)} for a,b,c in zip(fpr,tpr,thresholds))
    return roc_auc, pr_auc

def generate_figures(rows, nis_samples, target_dir):
    # Figures are generated only from the frozen CSV rows produced by this run.
    y = np.array([r["y_true"] for r in rows]); scores = np.array([r["s_comp"] for r in rows]); fd = os.path.join(target_dir,"figures")
    fpr,tpr,_=roc_curve(y,scores); ra=auc(fpr,tpr)
    plt.figure(figsize=(6,5),dpi=300); plt.plot(fpr,tpr,lw=2,label=f"Composite score (AUC={ra:.4f})"); plt.plot([0,1],[0,1],"--",lw=1)
    plt.xlabel("False Positive Rate"); plt.ylabel("True Positive Rate"); plt.legend(); plt.tight_layout(); plt.savefig(os.path.join(fd,"fig1_roc_curve.png")); plt.close()
    p,r,_=precision_recall_curve(y,scores); pa=auc(r,p)
    plt.figure(figsize=(6,5),dpi=300); plt.plot(r,p,lw=2,label=f"PR curve (AUC={pa:.4f})"); plt.xlabel("Recall"); plt.ylabel("Precision"); plt.legend(); plt.tight_layout(); plt.savefig(os.path.join(fd,"fig2_pr_curve.png")); plt.close()
    names=["K=2","K=1","NIS","CUSUM","Jitter","Sequential"]; preds=[[r[c] for r in rows] for c in ["d_k2","d_k1","a_nis","a_cusum","a_jitter","a_seq"]]
    vals=[[precision_score(y,p,zero_division=0),recall_score(y,p,zero_division=0),f1_score(y,p,zero_division=0)] for p in preds]
    x=np.arange(len(names)); w=.25; plt.figure(figsize=(9,5),dpi=300)
    for j,label in enumerate(["Precision","Recall","F1"]): plt.bar(x+(j-1)*w,[v[j] for v in vals],w,label=label)
    plt.xticks(x,names); plt.ylim(0,1.05); plt.ylabel("Score"); plt.legend(); plt.tight_layout(); plt.savefig(os.path.join(fd,"fig3_detector_comparison.png")); plt.close()
    for c, rows_c in [("case", None)]: pass
    plt.figure(figsize=(7,5),dpi=300)
    cases=[]; f1s=[]
    for c in CASES:
        rr=[r for r in rows if r["case"]==c]; yy=[r["y_true"] for r in rr]; pp=[r["d_k2"] for r in rr]
        cases.append(c); f1s.append(f1_score(yy,pp,zero_division=0))
    plt.bar(cases,f1s); plt.ylim(0,1.05); plt.ylabel("K=2 F1-score"); plt.tight_layout(); plt.savefig(os.path.join(fd,"fig4_casewise_f1.png")); plt.close()
    nis=np.asarray(nis_samples["case9"]); grid=np.linspace(0,max(70,float(np.max(nis))*1.1),250); plt.figure(figsize=(7,5),dpi=300)
    plt.hist(nis,bins=30,density=True,alpha=.6,label="Empirical benign NIS"); plt.plot(grid,chi2.pdf(grid,df=27),lw=2,label="Chi-square reference (df=27)")
    plt.axvline(chi2.ppf(.99,df=27),ls="--",label="99% threshold"); plt.xlabel("NIS"); plt.ylabel("Density"); plt.legend(); plt.tight_layout(); plt.savefig(os.path.join(fd,"fig5_nis_distribution.png")); plt.close()

def independent_verification(det_csv_path):
    rows=list(csv.DictReader(open(det_csv_path))); y=np.array([int(r["y_true"]) for r in rows]); p=np.array([int(r["d_k2"]) for r in rows])
    return calculate_metrics(y,p)

def generate_sha256sums(target_dir):
    lines=[]
    for root,_,files in os.walk(target_dir):
        for name in sorted(files):
            if name=="SHA256SUMS.txt": continue
            path=os.path.join(root,name); h=hashlib.sha256(open(path,"rb").read()).hexdigest(); lines.append(f"{h}  {os.path.relpath(path,target_dir)}")
    with open(os.path.join(target_dir,"SHA256SUMS.txt"),"w") as f: f.write("\n".join(lines)+"\n")

if __name__ == "__main__":
    out=sys.argv[1] if len(sys.argv)>1 else DEFAULT_OUTPUT_DIR
    rows,nis=run_experiment(SEED,out); roc,pr=generate_tables(rows,out); generate_figures(rows,nis,out)
    m=independent_verification(os.path.join(out,"metrics","detector_outputs.csv")); generate_sha256sums(out)
    print(f"PHYSICAL EXPERIMENT COMPLETE | ROC-AUC={roc:.6f} PR-AUC={pr:.6f} K2-F1={m['F1']:.6f} K2-Recall={m['Recall']:.6f}")
