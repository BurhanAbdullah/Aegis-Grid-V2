#!/usr/bin/env python3
"""Generate publication figures from the authoritative validation package.

All scientific values are read from authoritative CSVs; this script contains no
hard-coded experimental metrics. Figures are designed for IEEE Transactions use:
explicit units, sample sizes, uncertainty, informative legends, annotations, and
reproducible source metadata.
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
    precision = tp / (tp + fp) if tp + fp else 0.0
    return {"F1": f1, "Recall": recall, "FPR": fpr, "Precision": precision,
            "TN": tn, "FP": fp, "FN": fn, "TP": tp}


def style_axis(ax):
    ax.grid(axis="y", alpha=0.22, linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def annotate_bars(ax, bars, fmt="{:.3f}", dy=0.012):
    top = ax.get_ylim()[1]
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + dy * top,
                fmt.format(h), ha="center", va="bottom", fontsize=7)


def save(fig, stem):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(FIG / f"{stem}.png", dpi=400, bbox_inches="tight")
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
    n_pos = int(y.sum()); n_neg = int(len(y) - n_pos)

    # Fig. 1: method-level comparison on the complete authoritative detector trace.
    methods = [("NIS", nis), ("CUSUM", cusum), ("Jitter", jitter),
               ("Sequential", seq), ("K=1", k1), ("K=2", k2)]
    vals = [metrics(y, p) for _, p in methods]; x = np.arange(len(methods)); w = 0.25
    fig, ax = plt.subplots(figsize=(7.4, 4.35))
    b1 = ax.bar(x-w, [m["F1"] for m in vals], w, label="F1-score")
    b2 = ax.bar(x, [m["Recall"] for m in vals], w, label="Recall")
    b3 = ax.bar(x+w, [m["FPR"] for m in vals], w, label="False-positive rate")
    ax.set_ylabel("Rate / score"); ax.set_ylim(0, 1.16)
    ax.set_xticks(x); ax.set_xticklabels([n.replace(" ", "\n") for n, _ in methods])
    ax.set_title(f"Fig. 1 — Overall Detection Performance (N={len(rows):,}; {n_pos:,} positive, {n_neg:,} negative)")
    ax.legend(ncol=3, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.13), frameon=False)
    style_axis(ax); annotate_bars(ax, b1); annotate_bars(ax, b2); annotate_bars(ax, b3)
    fig.subplots_adjust(bottom=0.22); save(fig, "fig1_overall_performance")

    # Fig. 2: show every seed, then the five-seed mean and SD; K=1 is a primary-trace point.
    multi = read_csv(MULTI)
    k2_fpr = np.array([float(r["FPR"]) for r in multi]); k2_rec = np.array([float(r["Recall"]) for r in multi]); k2_f1 = np.array([float(r["F1"]) for r in multi])
    k1m = metrics(y, k1)
    fig, ax = plt.subplots(figsize=(6.5, 4.55))
    ax.scatter(k2_fpr, k2_rec, s=42, alpha=0.75, label="K=2: individual seeds (n=5)")
    ax.errorbar([k2_fpr.mean()], [k2_rec.mean()], xerr=[k2_fpr.std(ddof=1)], yerr=[k2_rec.std(ddof=1)],
                fmt="o", markersize=7, capsize=5, label=f"K=2 mean ± SD (F1={k2_f1.mean():.4f}±{k2_f1.std(ddof=1):.4f})")
    ax.scatter([k1m["FPR"]], [k1m["Recall"]], marker="D", s=70,
               label=f"K=1 primary (Recall={k1m['Recall']:.4f}, FPR={k1m['FPR']:.4f})")
    ax.set_xlabel("False-positive rate"); ax.set_ylabel("Recall")
    ax.set_title("Fig. 2 — Quorum Operating-Point Trade-off")
    ax.set_xlim(left=0); ax.set_ylim(0.70, 1.02)
    ax.legend(fontsize=7.5, loc="lower right", frameon=False); style_axis(ax)
    ax.text(0.02, 0.02, "K=1: OR gate; K=2: strict majority of three detectors",
            transform=ax.transAxes, fontsize=7, va="bottom")
    save(fig, "fig2_k1_vs_k2_tradeoff")

    # Fig. 3: threshold-independent ROC with class counts and AUC.
    fpr, tpr, _ = roc_curve(y, score); roc_auc = auc(fpr, tpr)
    fig, ax = plt.subplots(figsize=(5.8, 4.45))
    ax.plot(fpr, tpr, lw=2.2, label=f"Composite score $S_{{comp}}$ (ROC-AUC={roc_auc:.4f})")
    ax.plot([0, 1], [0, 1], "k--", lw=1.0, label="Chance")
    ax.set_xlabel("False-positive rate"); ax.set_ylabel("True-positive rate (recall)")
    ax.set_title(f"Fig. 3 — Threshold-Independent ROC (N={len(y):,})")
    ax.legend(loc="lower right", fontsize=8, frameon=False); style_axis(ax)
    ax.text(0.03, 0.04, f"Positive={n_pos:,}; Negative={n_neg:,}", transform=ax.transAxes, fontsize=8)
    save(fig, "fig3_roc_curve")

    # Fig. 4: precision-recall, with positive prevalence explicitly stated.
    precision, recall, _ = precision_recall_curve(y, score); pr_auc = auc(recall, precision)
    fig, ax = plt.subplots(figsize=(5.8, 4.45))
    ax.plot(recall, precision, lw=2.2, label=f"Composite score $S_{{comp}}$ (PR-AUC={pr_auc:.4f})")
    ax.axhline(n_pos / len(y), ls="--", lw=1.0, label=f"Prevalence baseline={n_pos/len(y):.3f}")
    ax.set_xlabel("Recall"); ax.set_ylabel("Precision")
    ax.set_title(f"Fig. 4 — Precision–Recall Curve (N={len(y):,})")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.02); ax.legend(loc="lower left", fontsize=8, frameon=False); style_axis(ax)
    save(fig, "fig4_pr_curve")

    # Fig. 5: five-seed casewise performance with 95% CI from the authoritative CSV.
    case = read_csv(CASEWISE); names = [r["case"].upper() for r in case]
    f1m = np.array([float(r["mean_F1"]) for r in case]); f1s = np.array([float(r["SD_F1"]) for r in case])
    ci = np.array([[float(r["CI_95_F1"].split(",")[0].strip("[")) for r in case],
                    [float(r["CI_95_F1"].split(",")[1].strip(" ]")) for r in case]])
    yerr = np.vstack([f1m - ci[0], ci[1] - f1m])
    fig, ax = plt.subplots(figsize=(6.5, 4.25)); x = np.arange(len(names))
    bars = ax.bar(x, f1m, yerr=yerr, capsize=5, label="F1 mean; error bars = 95% CI")
    ax.set_xticks(x); ax.set_xticklabels(names); ax.set_ylabel("F1-score (five-seed mean)"); ax.set_ylim(0.85, 1.02)
    ax.set_title("Fig. 5 — Topology-Wise Performance")
    ax.legend(fontsize=8, frameon=False); style_axis(ax); annotate_bars(ax, bars)
    ax.text(0.01, 0.01, "Each topology: 1,500 evaluations (300 per seed)", transform=ax.transAxes, fontsize=7.5)
    save(fig, "fig5_casewise_performance")

    # Fig. 6: attack-wise F1 and recall with 95% CI derived from the frozen CSV.
    attack = [r for r in read_csv(ATTACKWISE) if r["scenario"] != "baseline"]
    names = [r["scenario"].replace("_", " ").title() for r in attack]
    f1m = np.array([float(r["mean_F1"]) for r in attack]); f1s = np.array([float(r["SD_F1"]) for r in attack])
    recm = np.array([float(r["mean_Recall"]) for r in attack]); recs = np.array([float(r["SD_Recall"]) for r in attack])
    f1ci = np.array([[float(r["CI_95_F1"].split(",")[0].strip("[")) for r in attack], [float(r["CI_95_F1"].split(",")[1].strip(" ]")) for r in attack]])
    x = np.arange(len(names)); w = 0.35
    fig, ax = plt.subplots(figsize=(7.0, 4.25))
    b1 = ax.bar(x-w/2, f1m, w, yerr=np.vstack([f1m-f1ci[0], f1ci[1]-f1m]), capsize=4, label="F1-score (95% CI)")
    b2 = ax.bar(x+w/2, recm, w, yerr=recs, capsize=4, label="Recall (SD)")
    ax.set_xticks(x); ax.set_xticklabels(names, rotation=12, ha="right"); ax.set_ylabel("Metric")
    ax.set_ylim(0.60, 1.08); ax.set_title("Fig. 6 — Attack-Wise Performance")
    ax.legend(ncol=2, fontsize=8, frameon=False); style_axis(ax); annotate_bars(ax, b1); annotate_bars(ax, b2)
    ax.text(0.01, 0.01, "Each scenario: 1,200 evaluations (240 per seed); baseline omitted from comparison", transform=ax.transAxes, fontsize=7.5)
    fig.subplots_adjust(bottom=0.22); save(fig, "fig6_attackwise_performance")

    # Fig. 10: severity robustness, preserving the empirical tier order in the data.
    tiers = {}
    for r in rows:
        if int(r["y_true"]) == 1:
            tiers.setdefault(r.get("severity_tier", "unknown"), []).append(int(r["d_k2"]))
    labels = list(tiers); rates = [float(np.mean(tiers[t])) for t in labels]; counts = [len(tiers[t]) for t in labels]
    fig, ax = plt.subplots(figsize=(6.8, 4.15)); x = np.arange(len(labels))
    bars = ax.bar(x, rates, label="K=2 detection rate")
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=20, ha="right"); ax.set_ylabel("Detection rate")
    ax.set_ylim(0, 1.08); ax.set_title("Fig. 10 — Detection Robustness Across Attack Severity")
    ax.legend(frameon=False, fontsize=8); style_axis(ax); annotate_bars(ax, bars)
    for i, n in enumerate(counts): ax.text(i, 0.02, f"n={n}", ha="center", va="bottom", fontsize=7)
    fig.subplots_adjust(bottom=0.22); save(fig, "fig10_severity_robustness")

    # Fig. 12: numerical AC consistency; annotate orders of magnitude and system size.
    physical = read_csv(PHYSICAL); names = [f"{r['case'].upper()}\n({r['buses']} bus)" for r in physical]
    hp = np.array([float(r["h_p_max_abs_error"]) for r in physical]); hq = np.array([float(r["h_q_max_abs_error"]) for r in physical]); bal = np.array([abs(float(r["power_balance_residual"])) for r in physical]); x = np.arange(len(names)); w = 0.25
    fig, ax = plt.subplots(figsize=(7.2, 4.35))
    b1 = ax.bar(x-w, hp, w, label="max $|\Delta P|$"); b2 = ax.bar(x, hq, w, label="max $|\Delta Q|$"); b3 = ax.bar(x+w, bal, w, label="$|$power-balance residual$|$")
    ax.set_yscale("log"); ax.set_xticks(x); ax.set_xticklabels(names); ax.set_ylabel("Absolute discrepancy (p.u.)")
    ax.set_title("Fig. 12 — Independent AC Power-Flow Consistency")
    ax.legend(ncol=3, fontsize=7.5, loc="upper center", bbox_to_anchor=(0.5, -0.12), frameon=False); style_axis(ax)
    for bars, vals_ in ((b1, hp), (b2, hq), (b3, bal)):
        for bar, value in zip(bars, vals_):
            ax.text(bar.get_x()+bar.get_width()/2, value*1.15, f"{value:.1e}", ha="center", va="bottom", fontsize=6.5, rotation=90)
    fig.subplots_adjust(bottom=0.24); save(fig, "fig12_ac_powerflow_consistency")

    manifest = {
        "source_directory": str(DATA.relative_to(ROOT)), "detector_rows": len(rows),
        "positive_samples": n_pos, "negative_samples": n_neg,
        "roc_auc_primary": roc_auc, "pr_auc_primary": pr_auc,
        "k1_primary": k1m,
        "k2_five_seed": {"F1_mean": float(k2_f1.mean()), "F1_sd": float(k2_f1.std(ddof=1)),
                         "Recall_mean": float(k2_rec.mean()), "Recall_sd": float(k2_rec.std(ddof=1)),
                         "FPR_mean": float(k2_fpr.mean()), "FPR_sd": float(k2_fpr.std(ddof=1))},
        "retained_figures": [f + ".pdf" for f in RETAINED],
        "figure_design": {"format": "PDF + 400 dpi PNG", "uncertainty": "authoritative CSV CI/SD", "legends": "explicit metric/source definitions"},
    }
    (FIG / "FIGURE_MANIFEST.md").write_text("# Authoritative publication figure manifest\n\n```json\n" + json.dumps(manifest, indent=2, sort_keys=True) + "\n```\n", encoding="utf-8")
    lines = []
    for path in sorted(FIG.glob("*")):
        if path.name == "SHA256SUMS.txt" or not path.is_file():
            continue
        lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
    (FIG / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated {len(RETAINED)} retained figures from {DATA.relative_to(ROOT)}")
    print(f"Primary ROC-AUC={roc_auc:.6f}; primary PR-AUC={pr_auc:.6f}")
    print(f"K=2 five-seed F1={k2_f1.mean():.6f} +/- {k2_f1.std(ddof=1):.6f}")


if __name__ == "__main__":
    main()
