#!/usr/bin/env python3
"""Regenerate publication figures that previously contained stale hard-coded claims."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
INDEP = ROOT / "results" / "independent_validation_run"
FIG = INDEP / "paper_figures"
FIG.mkdir(parents=True, exist_ok=True)


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fig2():
    rows = read_csv(INDEP / "metrics" / "detector_outputs.csv")
    y = np.array([int(r["y_true"]) for r in rows])
    k1 = np.array([int(r["a_nis"]) or int(r["a_cusum"]) or int(r["a_jitter"]) for r in rows])
    k2 = np.array([int(r["d_k2"]) for r in rows])

    def metrics(p):
        tn = np.sum((p == 0) & (y == 0)); fp = np.sum((p == 1) & (y == 0))
        fn = np.sum((p == 0) & (y == 1)); tp = np.sum((p == 1) & (y == 1))
        recall = tp / (tp + fn) if tp + fn else 0.0
        fpr = fp / (fp + tn) if fp + tn else 0.0
        f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0
        return f1, recall, fpr

    f1_1, rec_1, fpr_1 = metrics(k1)
    f1_2, rec_2, fpr_2 = metrics(k2)

    fig, ax = plt.subplots(figsize=(6.0, 4.2))
    ax.scatter([fpr_1], [rec_1], s=100, label=f"K=1 OR (Recall={rec_1:.4f}, FPR={fpr_1:.4f})")
    ax.scatter([fpr_2], [rec_2], s=100, label=f"K=2 majority (Recall={rec_2:.4f}, FPR={fpr_2:.4f})")
    ax.plot([fpr_1, fpr_2], [rec_1, rec_2], "k--", alpha=0.6)
    ax.set_xlabel("False Positive Rate (FPR)")
    ax.set_ylabel("Recall (True Positive Rate)")
    ax.set_title("Fig. 2 — K=1 vs K=2 Operating-Point Trade-off (Seed 2026)")
    ax.set_xlim(-0.05, max(0.70, fpr_1 + 0.05))
    ax.set_ylim(max(0.0, min(rec_1, rec_2) - 0.10), 1.05)
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "fig2_k1_vs_k2_tradeoff.pdf")
    fig.savefig(FIG / "fig2_k1_vs_k2_tradeoff.png")
    plt.close(fig)


def fig12():
    rows = read_csv(ROOT / "results" / "current_physical_sanity.csv")
    cases = [r["case"] for r in rows]
    residual = np.array([abs(float(r["power_balance_residual"])) for r in rows])
    hp = np.array([float(r["h_p_max_abs_error"]) for r in rows])
    hq = np.array([float(r["h_q_max_abs_error"]) for r in rows])
    max_err = np.maximum.reduce([residual, hp, hq])

    assert np.all(max_err < 1e-9), f"Physical validation exceeds tolerance: {max_err.max():.3e}"
    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    ax.semilogy(cases, max_err, marker="o", label="Maximum physical/model consistency error")
    ax.axhline(1e-9, linestyle="--", label="Acceptance threshold = $10^{-9}$")
    ax.set_xlabel("IEEE benchmark case")
    ax.set_ylabel("Absolute error")
    ax.set_title("Fig. 12 — AC Power-Flow and Measurement-Equation Consistency")
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "fig12_ac_powerflow_consistency.pdf")
    fig.savefig(FIG / "fig12_ac_powerflow_consistency.png")
    plt.close(fig)


def main():
    fig2()
    fig12()
    print("PUBLICATION FIGURE REGENERATION: PASS")


if __name__ == "__main__":
    main()
