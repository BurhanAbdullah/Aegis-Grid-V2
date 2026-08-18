#!/usr/bin/env python3
"""Verify the frozen publication snapshot before creating the final tag.

This is a release gate only: it never changes xmon-main or publication data.
It verifies that the authoritative result directory, paper figures, manuscript,
and validation provenance are present and that the manuscript points to the
frozen authoritative figure directory.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "authoritative_validation_20260815"
PAPER = ROOT / "paper" / "main.tex"

FIGURES = [
    "fig1_overall_performance.pdf",
    "fig2_k1_vs_k2_tradeoff.pdf",
    "fig3_roc_curve.pdf",
    "fig4_pr_curve.pdf",
    "fig5_casewise_performance.pdf",
    "fig6_attackwise_performance.pdf",
    "fig10_severity_robustness.pdf",
    "fig12_ac_powerflow_consistency.pdf",
]


def main() -> int:
    failures = []
    if not RESULTS.is_dir():
        failures.append(f"missing authoritative result directory: {RESULTS}")
    if not PAPER.is_file():
        failures.append(f"missing manuscript: {PAPER}")
    else:
        text = PAPER.read_text(encoding="utf-8")
        stale = "results/independent_validation_run"
        if stale in text:
            failures.append("manuscript still references stale independent_validation_run figures")
        if "results/authoritative_validation_20260815" not in text:
            failures.append("manuscript does not reference authoritative validation figures")
        # Do not flag historical claims merely because the manuscript explicitly
        # says they are archived/rejected. Flag only a live numerical claim that
        # is presented as authoritative in the current manuscript.
        historical_markers = (
            "does not retain",
            "earlier archived",
            "earlier high-recall",
            "stale",
            "archived claims",
        )
        for line in text.splitlines():
            if ("0.6" in line or "85.85" in line) and not any(
                marker in line.lower() for marker in historical_markers
            ):
                failures.append("manuscript contains an unqualified stale performance claim")
                break

    for figure in FIGURES:
        path = RESULTS / "paper_figures" / figure
        if not path.is_file() or path.stat().st_size == 0:
            failures.append(f"missing/empty publication figure: {path}")

    if failures:
        print("PUBLICATION SNAPSHOT VERIFICATION: FAIL")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print("PUBLICATION SNAPSHOT VERIFICATION: PASS")
    print(f"authoritative source: {RESULTS.relative_to(ROOT)}")
    print(f"figures verified: {len(FIGURES)}")
    print("main branch is not modified by this verifier")
    return 0


if __name__ == "__main__":
    sys.exit(main())
