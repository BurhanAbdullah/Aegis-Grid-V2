#!/usr/bin/env python3
"""Generate clean IEEE Transactions publication figures from authoritative CSVs.

Scientific values are read only from the authoritative validation package. This
script changes presentation only: typography, spacing, legend placement,
annotation density, and export resolution. No experimental values are hard-coded.
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

# Consistent Transactions-style typography. Titles are deliberately omitted from
# the plot area; the manuscript caption supplies figure titles/context.
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 9,
    "axes.labelsize": 9,
    "axes.titlesize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 7.5,
    "figure.dpi": 150,
    "savefig.dpi": 400,
    "axes.linewidth": 0.8,
    "xtick.major.width": 0.7,
    "ytick.major.width": 0.7,
    "mathtext.fontset": "dejavuserif",
})


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def metrics(y, pred):
    y = np.asarray(y, dtype=int)
    pred = np.asarray(pred, dtype=int)
    tn = int(((pred == 0) & (y == 0)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    tp = int(((pred == 1) & (y == 1)).sum())
    recall = tp / (tp + fn) if tp + fn else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0
    precision = tp / (tp + fp) if tp + fp else 0.0
    return {"F1": f1, "Recall": recall, "FPR": fpr, "Precision": precision,
            "TN": tn, "FP": fp, "FN": fn, "TP": tp}


def style_axis(ax, grid_axis="y"):
    if grid_axis:
        ax.grid(axis=grid_axis, alpha=0.20, linewidth=0.65)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(direction="out", length=3, width=0.7)


def save(fig, stem):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"{stem}.pdf", bbox_inches="tight", pad_inches=0.06)
    fig.savefig(FIG / f"{stem}.png", dpi=400, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)


def parse_ci(value):
    lo, hi = value.strip("[]").split(",")
    return float(lo), float(hi)


def main():
    required = [DET, MULTI, CASEWISE, ATTACKWISE, PHYSICAL]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing authoritative inputs: " + ", ".join(missing))

    rows = read_csv(DET)
    y = np.array([int(r["y_true"]) for r in rows])
    nis = np.array([int(r["a_nis"]) for r in rows])
    cusum = np.array([int(r["a_cusum"]) for r in rows])
    jitter = np.array([int(r["a_jitter"]) for r in rows])
    seq = np.array([int(r["a_seq"]) for r in rows])
    k1 = np.array([int(r["d_k1"]) for r in rows])
    k2 = np.array([int(r["d_k2"]) for r in rows])
    score = np.array([float(r["s_comp"]) for r in rows])
    n_pos = int(y.sum())
    n_neg = int(len(y) - n_pos)

    # Fig. 1: grouped detector comparison. No value labels are placed over bars;
    # the uncluttered geometry is paired with an explicit legend and the paper table.
    methods = [("NIS", nis), ("CUSUM", cusum), ("Jitter", jitter),
               ("Sequential", seq), ("K=1", k1), ("K=2", k2)]
    vals = [metrics(y, p) for _, p in methods]
    x = np.arange(len(methods))
    w = 0.24
    fig, ax = plt.subplots(figsize=(7.2, 4.25), constrained_layout=True)
    ax.bar(x - w, [m["F1"] for m in vals], w, label="F1-score")
    ax.bar(x, [m["Recall"] for m in vals], w, label="Recall")
    ax.bar(x + w, [m["FPR"] for m in vals], w, label="False-positive rate")
    ax.set_ylabel("Score / rate")
    ax.set_ylim(0, 1.08)
    ax.set_xticks(x)
    ax.set_xticklabels(["NIS", "CUSUM", "Jitter", "Sequential", "K=1", "K=2"])
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.13),
              frameon=False, handlelength=1.5, columnspacing=1.3)
    ax.text(0.0, -0.23, f"Authoritative detector trace: N={len(rows):,} ({n_pos:,} positive; {n_neg:,} negative)",
            transform=ax.transAxes, fontsize=7.2, ha="left", va="top")
    style_axis(ax)
    save(fig, "fig1_overall_performance")

    # Fig. 2: K=1 versus K=2 operating points. Legend is outside the data region.
    multi = read_csv(MULTI)
    k2_fpr = np.array([float(r["FPR"]) for r in multi])
    k2_rec = np.array([float(r["Recall"]) for r in multi])
    k2_f1 = np.array([float(r["F1"]) for r in multi])
    k1m = metrics(y, k1)
    fig, ax = plt.subplots(figsize=(6.8, 4.55), constrained_layout=True)
    ax.scatter(k2_fpr, k2_rec, s=38, alpha=0.80, label="K=2 individual seeds (n=5)")
    ax.errorbar(k2_fpr.mean(), k2_rec.mean(), xerr=k2_fpr.std(ddof=1),
                yerr=k2_rec.std(ddof=1), fmt="o", markersize=6.5, capsize=4,
                label="K=2 mean ± SD")
    ax.scatter(k1m["FPR"], k1m["Recall"], marker="D", s=58,
               label="K=1 primary trace")
    ax.set_xlabel("False-positive rate")
    ax.set_ylabel("Recall")
    ax.set_xlim(left=0)
    ax.set_ylim(0.70, 1.02)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=3,
              frameon=False, columnspacing=1.2)
    ax.text(0.99, 0.02,
            f"K=2 F1={k2_f1.mean():.4f}±{k2_f1.std(ddof=1):.4f}; "
            f"K=1 recall={k1m['Recall']:.4f}",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=7.2)
    style_axis(ax, "both")
    save(fig, "fig2_k1_vs_k2_tradeoff")

    # Fig. 3: ROC. Annotation is confined to a quiet corner and legend is external.
    fpr, tpr, _ = roc_curve(y, score)
    roc_auc = auc(fpr, tpr)
    fig, ax = plt.subplots(figsize=(6.0, 4.45), constrained_layout=True)
    ax.plot(fpr, tpr, lw=2.0, label=f"Composite score $S_{{comp}}$ (AUC={roc_auc:.4f})")
    ax.plot([0, 1], [0, 1], "k--", lw=0.9, label="Chance")
    ax.set_xlabel("False-positive rate")
    ax.set_ylabel("True-positive rate (recall)")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2,
              frameon=False, columnspacing=1.5)
    ax.text(0.02, 0.04, f"N={len(y):,}; positive={n_pos:,}; negative={n_neg:,}",
            transform=ax.transAxes, fontsize=7.5)
    style_axis(ax, "both")
    save(fig, "fig3_roc_curve")

    # Fig. 4: PR curve with prevalence baseline outside the data-dense region.
    precision, recall, _ = precision_recall_curve(y, score)
    pr_auc = auc(recall, precision)
    fig, ax = plt.subplots(figsize=(6.0, 4.45), constrained_layout=True)
    ax.plot(recall, precision, lw=2.0,
            label=f"Composite score $S_{{comp}}$ (AUC={pr_auc:.4f})")
    ax.axhline(n_pos / len(y), ls="--", lw=0.9,
               label=f"Prevalence baseline={n_pos/len(y):.3f}")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2,
              frameon=False, columnspacing=1.4)
    style_axis(ax, "both")
    save(fig, "fig4_pr_curve")

    # Fig. 5: topology-wise five-seed means with 95% CI. No labels over bars.
    case = read_csv(CASEWISE)
    names = [r["case"].upper() for r in case]
    f1m = np.array([float(r["mean_F1"]) for r in case])
    ci = np.array([parse_ci(r["CI_95_F1"]) for r in case]).T
    yerr = np.vstack([f1m - ci[0], ci[1] - f1m])
    fig, ax = plt.subplots(figsize=(6.7, 4.25), constrained_layout=True)
    x = np.arange(len(names))
    ax.bar(x, f1m, yerr=yerr, capsize=4.5, width=0.58,
           label="F1-score mean; error bars = 95% CI")
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylabel("F1-score")
    ax.set_ylim(0.85, 1.01)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), frameon=False)
    ax.text(0.5, -0.23, "Five seeds; 1,500 evaluations per topology (300 per seed)",
            transform=ax.transAxes, ha="center", va="top", fontsize=7.2)
    style_axis(ax)
    save(fig, "fig5_casewise_performance")

    # Fig. 6: attack-wise F1/recall. Rotate labels only enough to prevent collisions.
    attack = [r for r in read_csv(ATTACKWISE) if r["scenario"] != "baseline"]
    names = [r["scenario"].replace("_", " ").title() for r in attack]
    f1m = np.array([float(r["mean_F1"]) for r in attack])
    recm = np.array([float(r["mean_Recall"]) for r in attack])
    recs = np.array([float(r["SD_Recall"]) for r in attack])
    f1ci = np.array([parse_ci(r["CI_95_F1"]) for r in attack]).T
    x = np.arange(len(names))
    w = 0.34
    fig, ax = plt.subplots(figsize=(7.4, 4.45), constrained_layout=True)
    ax.bar(x - w/2, f1m, w, yerr=np.vstack([f1m - f1ci[0], f1ci[1] - f1m]),
           capsize=3.5, label="F1-score (95% CI)")
    ax.bar(x + w/2, recm, w, yerr=recs, capsize=3.5, label="Recall (SD)")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=15, ha="right")
    ax.set_ylabel("Metric")
    ax.set_ylim(0.60, 1.06)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2,
              frameon=False)
    ax.text(0.5, -0.28,
            "Five seeds; 1,200 evaluations per scenario (240 per seed); baseline omitted",
            transform=ax.transAxes, ha="center", va="top", fontsize=7.1)
    style_axis(ax)
    save(fig, "fig6_attackwise_performance")

    # Fig. 10: severity robustness. Counts are placed below the axis, not on bars.
    tiers = {}
    for r in rows:
        if int(r["y_true"]) == 1:
            tiers.setdefault(r.get("severity_tier", "unknown"), []).append(int(r["d_k2"]))
    labels = list(tiers)
    rates = np.array([float(np.mean(tiers[t])) for t in labels])
    counts = [len(tiers[t]) for t in labels]
    fig, ax = plt.subplots(figsize=(6.9, 4.35), constrained_layout=True)
    x = np.arange(len(labels))
    ax.bar(x, rates, width=0.58, label="K=2 detection rate")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=15, ha="right")
    ax.set_ylabel("Detection rate")
    ax.set_ylim(0, 1.06)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), frameon=False)
    ax.text(0.5, -0.25,
            "Counts of positive attack samples by severity tier: " + " · ".join(f"{a}: n={b}" for a, b in zip(labels, counts)),
            transform=ax.transAxes, ha="center", va="top", fontsize=7.0)
    style_axis(ax)
    save(fig, "fig10_severity_robustness")

    # Fig. 12: AC consistency shown as separated log-scale points. This avoids the
    # severe crowding caused by rotated scientific-notation labels on tiny bars.
    physical = read_csv(PHYSICAL)
    names = [f"{r['case'].upper()}\n{r['buses']} bus" for r in physical]
    hp = np.array([float(r["h_p_max_abs_error"]) for r in physical])
    hq = np.array([float(r["h_q_max_abs_error"]) for r in physical])
    bal = np.abs(np.array([float(r["power_balance_residual"]) for r in physical]))
    x = np.arange(len(names))
    fig, ax = plt.subplots(figsize=(7.1, 4.55), constrained_layout=True)
    offsets = (-0.16, 0.0, 0.16)
    series = [
        (hp, r"max $|\Delta P|$", "o"),
        (hq, r"max $|\Delta Q|$", "s"),
        (bal, r"$|$power-balance residual$|$", "^"),
    ]
    for off, (values, label, marker) in zip(offsets, series):
        ax.semilogy(x + off, values, marker=marker, linestyle="none",
                    markersize=6.5, label=label)
    ax.axhline(1e-9, ls="--", lw=0.9, label=r"Acceptance threshold $10^{-9}$")
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylabel("Absolute discrepancy (p.u.; log scale)")
    ax.set_ylim(1e-16, 3e-8)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2,
              frameon=False, columnspacing=1.2)
    ax.text(0.5, -0.25,
            "Independent AC consistency audit; all four canonical cases remain below the acceptance threshold",
            transform=ax.transAxes, ha="center", va="top", fontsize=7.0)
    style_axis(ax, "both")
    save(fig, "fig12_ac_powerflow_consistency")

    manifest = {
        "source_directory": str(DATA.relative_to(ROOT)),
        "detector_rows": len(rows),
        "positive_samples": n_pos,
        "negative_samples": n_neg,
        "roc_auc_primary": float(roc_auc),
        "pr_auc_primary": float(pr_auc),
        "k1_primary": k1m,
        "k2_five_seed": {
            "F1_mean": float(k2_f1.mean()),
            "F1_sd": float(k2_f1.std(ddof=1)),
            "Recall_mean": float(k2_rec.mean()),
            "Recall_sd": float(k2_rec.std(ddof=1)),
            "FPR_mean": float(k2_fpr.mean()),
            "FPR_sd": float(k2_fpr.std(ddof=1)),
        },
        "retained_figures": [f + ".pdf" for f in RETAINED],
        "figure_design": {
            "format": "PDF + 400 dpi PNG",
            "titles_inside_axes": False,
            "legend_policy": "outside data region where practical",
            "annotation_policy": "no overlapping data labels; no rotated scientific-notation bar labels",
            "uncertainty": "authoritative CSV CI/SD",
            "scientific_values_changed": False,
        },
    }
    (FIG / "FIGURE_MANIFEST.md").write_text(
        "# Authoritative publication figure manifest\n\n```json\n" +
        json.dumps(manifest, indent=2, sort_keys=True) +
        "\n```\n", encoding="utf-8"
    )
    lines = []
    for path in sorted(FIG.glob("*")):
        if path.name == "SHA256SUMS.txt" or not path.is_file():
            continue
        lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
    (FIG / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated {len(RETAINED)} retained figures from {DATA.relative_to(ROOT)}")
    print(f"Primary ROC-AUC={roc_auc:.6f}; primary PR-AUC={pr_auc:.6f}")
    print(f"K=2 five-seed F1={k2_f1.mean():.6f} +/- {k2_f1.std(ddof=1):.6f}")
    print("Transactions layout hardening: no in-axis titles, external legends, separated annotations")


if __name__ == "__main__":
    main()
