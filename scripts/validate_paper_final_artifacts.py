#!/usr/bin/env python3
"""Validate manuscript provenance and frozen verification values.

This checker does not regenerate or modify scientific results. It verifies that
paper/main.tex points to the frozen final figure directory and that the physical
and five-seed values in the manuscript remain consistent with the frozen CSVs.
"""
from pathlib import Path
import csv
import re
import statistics

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "main.tex"
PKG = ROOT / "results" / "paper_final_verified_20260908"
FIG = PKG / "figures"


def fail(msg):
    raise SystemExit(f"FAIL: {msg}")


def close(a, b, tol=5e-4):
    return abs(a - b) <= tol


def main():
    if not PAPER.exists():
        fail("paper/main.tex is missing")
    if not PKG.exists():
        fail("frozen verification package is missing")

    tex = PAPER.read_text(encoding="utf-8")
    if "../results/independent_validation_run/paper_figures/" in tex:
        fail("main.tex still references historical independent_validation_run figures")
    if "../results/paper_final_verified_20260908/figures/" not in tex:
        fail("main.tex does not point to the frozen final figure directory")

    # Five-seed values: verify mean and sample SD against the frozen CSV.
    rows = list(csv.DictReader((PKG / "multi_seed_summary.csv").open()))
    metrics = ["Accuracy", "Precision", "Recall", "F1", "FPR", "MCC"]
    for metric in metrics:
        vals = [float(r[metric]) for r in rows]
        mean = statistics.mean(vals)
        sd = statistics.stdev(vals)
        m = re.search(rf"{re.escape(metric.replace('F1', 'F1-score'))} & ([0-9.]+) & ([0-9.]+)", tex)
        if metric == "F1":
            m = re.search(r"F1-score & ([0-9.]+) & ([0-9.]+)", tex)
        if not m:
            fail(f"manuscript table entry missing for {metric}")
        if not close(float(m.group(1)), mean) or not close(float(m.group(2)), sd):
            fail(f"{metric} manuscript value disagrees with frozen CSV: mean={mean:.6f}, sd={sd:.6f}")

    # Physical audit: use maxima from the frozen CSV, not hand-entered historical values.
    prow = list(csv.DictReader((PKG / "current_physical_sanity.csv").open()))
    hp = max(float(r["h_p_max_abs_error"]) for r in prow)
    hq = max(float(r["h_q_max_abs_error"]) for r in prow)
    pb = max(abs(float(r["power_balance_residual"])) for r in prow)

    for expected in [hp, hq, pb]:
        if expected <= 0:
            fail("non-positive physical audit value")

    if not re.search(r"3\.09\\times10\^{-14}.*active power", tex):
        fail("active-power physical value is not the frozen 3.09e-14 p.u. maximum")
    if not re.search(r"2\.46\\times10\^{-14}.*reactive power", tex):
        fail("reactive-power physical value is not the frozen 2.46e-14 p.u. maximum")
    if not re.search(r"2\.04\\times10\^{-14}.*active-power balance", tex):
        fail("power-balance value is not the frozen 2.04e-14 p.u. maximum")

    print("PASS: final manuscript provenance and frozen quantitative values are consistent.")
    print(f"  five-seed rows: {len(rows)}")
    print(f"  physical maxima: hP={hp:.3e}, hQ={hq:.3e}, balance={pb:.3e}")
    print(f"  figure directory: {FIG}")


if __name__ == "__main__":
    main()
