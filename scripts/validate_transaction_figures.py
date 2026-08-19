#!/usr/bin/env python3
"""Release gate for publication-figure completeness and provenance."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "results" / "authoritative_validation_20260815" / "paper_figures"
PAPER = ROOT / "paper" / "main.tex"

FIGURES = [
    "fig1_overall_performance", "fig2_k1_vs_k2_tradeoff", "fig3_roc_curve",
    "fig4_pr_curve", "fig5_casewise_performance", "fig6_attackwise_performance",
    "fig10_severity_robustness", "fig12_ac_powerflow_consistency",
]

REQUIRED_CAPTION_TERMS = [
    "authoritative", "five-seed", "95\\%", "6,000", "composite threat score",
]


def main() -> None:
    failures = []
    if not FIG.is_dir():
        failures.append(f"missing figure directory: {FIG}")
    else:
        for stem in FIGURES:
            pdf = FIG / f"{stem}.pdf"
            png = FIG / f"{stem}.png"
            if not pdf.is_file() or pdf.stat().st_size < 1000:
                failures.append(f"missing/empty PDF: {pdf}")
            if not png.is_file() or png.stat().st_size < 1000:
                failures.append(f"missing/empty PNG: {png}")
    text = PAPER.read_text(encoding="utf-8")
    for term in REQUIRED_CAPTION_TERMS:
        if term not in text:
            failures.append(f"manuscript missing Transactions figure/provenance term: {term}")
    if "FIGURE_MANIFEST.md" not in str((FIG / "FIGURE_MANIFEST.md")):
        failures.append("figure manifest path check failed")
    if failures:
        print("TRANSACTIONS FIGURE QUALITY GATE: FAIL")
        for f in failures:
            print(" - " + f)
        raise SystemExit(1)
    print("TRANSACTIONS FIGURE QUALITY GATE: PASS")
    print(f"verified figures: {len(FIGURES)} PDFs + {len(FIGURES)} PNGs")
    print("captions/provenance metadata present")


if __name__ == "__main__":
    main()
