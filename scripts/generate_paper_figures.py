#!/usr/bin/env python3
"""Generate retained publication figures from one authoritative CSV package.

No publication metric is hard-coded. Every displayed scientific value is computed
from results/authoritative_validation_20260815 or its frozen summary CSVs.
"""
from pathlib import Path
import csv
import hashlib
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import auc, precision_recall_curve, roc_curve

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "results" / "authoritative_validation_20260815"
FIG = DATA / "paper_figures"
DET = DATA / "metrics" / "detector_outputs.csv"
MULTI = DATA / "multi_seed_summary.csv"
CASEWISE = DATA / "casewise_5seed.csv"
ATTACKWISE = DATA / "attackwise_5seed.csv"
PHYSICAL = DATA / "physical_sanity.csv"

RETAINED = [
    "fig1_overall_performance", "fig2_k1_vs_k2_tradeoff", "fig3_roc_curve",
    "fig4_pr_curve", "fig5_casewise_performance", "fig6_attackwise_performance",
    "fig10_severity_robustness", "fig12_ac_powerflow_consistency",
]


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def metrics(y, pred):
    y = np.asarray(y, dtype=int); pred = np.asarray(pred, dtype=int)
    tn = int(((pred == 0) & (y == 0)).sum()); fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum()); tp = int(((pred == 1) & (y == 1)).sum())
    recall = tp / (tp + fn) if tp + fn else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0
    return {"F1": f1, "Recall": recall, "FPR": fpr, "TN": tn, "FP": fp, "FN": fn, "TP": tp}


def save(fig, stem):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(FIG / f"{stem}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    required = [DET, MULTI, CASEWISE, ATTACKWISE, PHYSICAL]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing authoritative inputs: " + ", ".join(missing))

    rows = read_csv(DET)
    y = np.array([int(r["y_true"]) for r in rows])
    nis = np.array([int(r["a_nis"]) for r in rows]); cusum = np.array([int(r["a_cusum"]) for r in rows])
    jitter = np.array([int(r["a_jitter"]) for r in rows]); seq = np.array([int(r["a_seq"]) for r in rows])
    k1 = np.array([int(r["d_k1"]) for r in rows]); k2 = np.array([int(r["d_k2"]) for r in rows])
    score = np.array([float(r["s_comp"]) for r in rows])

    # Fig. 1: primary detector trace.
    methods = [("NIS", nis), ("CUSUM", cusum), ("Jitter", jitter), ("Sequential", seq), ("K=1", k1), ("K=2", k2)]
    vals = [metrics(y, p) for _, p in methods]; x = np.arange(len(methods)); w = 0.25
    fig, ax = plt.subplots(figsize=(7.5, 4.0))
    ax.bar(x-w, [m["F1"] for m in vals], w, label="F1"); ax.bar(x, [m["Recall"] for m in vals], w, label="Recall"); ax.bar(x+w, [m["FPR"] for m in vals], w, label="FPR")
    ax.set_ylabel("Metric"); ax.set_ylim(0, 1.15); ax.set_xticks(x); ax.set_xticklabels([n.replace(" ", "\n") for n, _ in methods]); ax.set_title(f"Fig. 1 — Overall Detection Performance (N={len(rows):,})"); ax.legend(); save(fig, "fig1_overall_performance")

    # Fig. 2: K=1 primary trace; K=2 five-seed summary.
    multi = read_csv(MULTI); k2_fpr = np.array([float(r["FPR"]) for r in multi]); k2_rec = np.array([float(r["Recall"]) for r in multi]); k2_f1 = np.array([float(r["F1"]) for r in multi]); k1m = metrics(y, k1)
    fig, ax = plt.subplots(figsize=(6.2, 4.2)); ax.scatter([k1m["FPR"]], [k1m["Recall"]], s=100, label=f"K=1 primary (Recall={k1m['Recall']:.4f}, FPR={k1m['FPR']:.4f})")
    ax.errorbar([k2_fpr.mean()], [k2_rec.mean()], xerr=[k2_fpr.std()], yerr=[k2_rec.std()], fmt="o", capsize=5, label=f"K=2 five-seed (F1={k2_f1.mean():.4f}±{k2_f1.std():.4f})")
    ax.set_xlabel("False Positive Rate"); ax.set_ylabel("Recall"); ax.set_title("Fig. 2 — K=1 vs K=2 Operating-Point Trade-off"); ax.set_xlim(left=0); ax.set_ylim(0.7, 1.02); ax.legend(fontsize=8); save(fig, "fig2_k1_vs_k2_tradeoff")

    # Fig. 3/4: threshold-independent curves directly from S_comp.
    fpr, tpr, _ = roc_curve(y, score); roc_auc = auc(fpr, tpr)
    fig, ax = plt.subplots(figsize=(5.5, 4.0)); ax.plot(fpr, tpr, lw=2, label=f"S_comp (ROC-AUC={roc_auc:.4f})"); ax.plot([0, 1], [0, 1], "k--", lw=1); ax.set_xlabel("False Positive Rate"); ax.set_ylabel("True Positive Rate"); ax.set_title("Fig. 3 — ROC Curve"); ax.legend(loc="lower right"); save(fig, "fig3_roc_curve")
    precision, recall, _ = precision_recall_curve(y, score); pr_auc = auc(recall, precision)
    fig, ax = plt.subplots(figsize=(5.5, 4.0)); ax.plot(recall, precision, lw=2, label=f"S_comp (PR-AUC={pr_auc:.4f})"); ax.set_xlabel("Recall"); ax.set_ylabel("Precision"); ax.set_title("Fig. 4 — Precision–Recall Curve"); ax.legend(loc="lower left"); save(fig, "fig4_pr_curve")

    # Fig. 5: frozen five-seed casewise summary.
    case = read_csv(CASEWISE); names = [r["case"].upper() for r in case]; f1m = np.array([float(r["mean_F1"]) for r in case]); f1s = np.array([float(r["SD_F1"]) for r in case])
    fig, ax = plt.subplots(figsize=(6.0, 3.8)); ax.bar(np.arange(len(names)), f1m, yerr=f1s, capsize=5); ax.set_xticks(np.arange(len(names))); ax.set_xticklabels(names); ax.set_ylabel("Mean F1 (5 seeds)"); ax.set_ylim(0.8, 1.05); ax.set_title("Fig. 5 — Case-Wise Performance"); save(fig, "fig5_casewise_performance")

    # Fig. 6: frozen five-seed attackwise summary.
    attack = [r for r in read_csv(ATTACKWISE) if r["scenario"] != "baseline"]; names = [r["scenario"].replace("_", " ").title() for r in attack]
    f1m = np.array([float(r["mean_F1"]) for r in attack]); f1s = np.array([float(r["SD_F1"]) for r in attack]); recm = np.array([float(r["mean_Recall"]) for r in attack]); recs = np.array([float(r["SD_Recall"]) for r in attack]); x = np.arange(len(names)); w = 0.35
    fig, ax = plt.subplots(figsize=(6.5, 3.8)); ax.bar(x-w/2, f1m, w, yerr=f1s, capsize=4, label="F1"); ax.bar(x+w/2, recm, w, yerr=recs, capsize=4, label="Recall"); ax.set_xticks(x); ax.set_xticklabels(names); ax.set_ylabel("Metric (5 seeds)"); ax.set_ylim(0.6, 1.08); ax.set_title("Fig. 6 — Attack-Wise Performance"); ax.legend(); save(fig, "fig6_attackwise_performance")

    # Fig. 10: severity from the primary trace, never a legacy artifact.
    tiers = {}
    for r in rows:
        if int(r["y_true"]) == 1:
            tiers.setdefault(r.get("severity_tier", "unknown"), []).append(int(r["d_k2"]))
    labels = list(tiers); rates = [float(np.mean(tiers[t])) for t in labels]
    fig, ax = plt.subplots(figsize=(6.5, 3.8)); ax.bar(np.arange(len(labels)), rates); ax.set_xticks(np.arange(len(labels))); ax.set_xticklabels(labels, rotation=25, ha="right"); ax.set_ylabel("K=2 detection rate"); ax.set_ylim(0, 1.05); ax.set_title("Fig. 10 — Detection Robustness Across Attack Severity"); save(fig, "fig10_severity_robustness")

    # Fig. 12: frozen physical-sanity summary.
    physical = read_csv(PHYSICAL); names = [r["case"].upper() for r in physical]; hp = np.array([float(r["h_p_max_abs_error"]) for r in physical]); hq = np.array([float(r["h_q_max_abs_error"]) for r in physical]); bal = np.array([abs(float(r["power_balance_residual"])) for r in physical]); x = np.arange(len(names)); w = 0.25
    fig, ax = plt.subplots(figsize=(7.0, 4.0)); ax.bar(x-w, hp, w, label="max |ΔP|"); ax.bar(x, hq, w, label="max |ΔQ|"); ax.bar(x+w, bal, w, label="|balance residual|"); ax.set_yscale("log"); ax.set_xticks(x); ax.set_xticklabels(names); ax.set_ylabel("Absolute discrepancy (p.u.)"); ax.set_title("Fig. 12 — AC Power-Flow Numerical Consistency"); ax.legend(); save(fig, "fig12_ac_powerflow_consistency")

    manifest = {"source_directory": str(DATA.relative_to(ROOT)), "detector_rows": len(rows), "roc_auc_primary": roc_auc, "pr_auc_primary": pr_auc, "k1_primary": k1m, "k2_five_seed": {"F1_mean": float(k2_f1.mean()), "F1_sd": float(k2_f1.std()), "Recall_mean": float(k2_rec.mean()), "Recall_sd": float(k2_rec.std()), "FPR_mean": float(k2_fpr.mean()), "FPR_sd": float(k2_fpr.std())}, "retained_figures": [f + ".pdf" for f in RETAINED]}
    (FIG / "FIGURE_MANIFEST.md").write_text("# Authoritative publication figure manifest\n\n```json\n" + json.dumps(manifest, indent=2, sort_keys=True) + "\n```\n", encoding="utf-8")
    lines = []
    for path in sorted(FIG.glob("*")):
        if path.name == "SHA256SUMS.txt" or not path.is_file(): continue
        lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
    (FIG / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated {len(RETAINED)} retained figures from {DATA.relative_to(ROOT)}")
    print(f"Primary ROC-AUC={roc_auc:.6f}; primary PR-AUC={pr_auc:.6f}")
    print(f"K=2 five-seed F1={k2_f1.mean():.6f} +/- {k2_f1.std():.6f}")


if __name__ == "__main__":
    main()
