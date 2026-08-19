#!/usr/bin/env python3
"""Final publication gate for the corrected XMON-Grid release candidate."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "main.tex"
BIB = ROOT / "paper" / "references.bib"
DATA = ROOT / "results" / "authoritative_validation_20260815"
MANIFEST = DATA / "paper_figures" / "FIGURE_MANIFEST.md"
RELEASE = ROOT / "RELEASE_20260814.md"
REQUIRED = [PAPER, BIB, MANIFEST, RELEASE, DATA / "metrics" / "detector_outputs.csv", DATA / "multi_seed_summary.csv", DATA / "casewise_5seed.csv", DATA / "attackwise_5seed.csv", DATA / "physical_sanity.csv"]
REQUIRED_FIGURES = [f"fig{i}.pdf" for i in ()]  # populated below for clarity
REQUIRED_FIGURES = [
    "fig1_overall_performance.pdf", "fig2_k1_vs_k2_tradeoff.pdf", "fig3_roc_curve.pdf", "fig4_pr_curve.pdf",
    "fig5_casewise_performance.pdf", "fig6_attackwise_performance.pdf", "fig10_severity_robustness.pdf", "fig12_ac_powerflow_consistency.pdf",
]
EXPECTED = [r"0\.9204\\pm0\.0026", r"0\.8850\\pm0\.0012", r"0\.1525\\pm0\.0197", r"0\.6667\\pm0\.0151"]
STALE = ["0.9232\\pm0.0032", "0.8585\\pm0.0048", "0.0058\\pm0.0073", "192.58", "85.85\\%"]


def main() -> int:
    failures = []
    for path in REQUIRED:
        if not path.exists(): failures.append(f"missing required publication file: {path.relative_to(ROOT)}")
    fig_dir = DATA / "paper_figures"
    for name in REQUIRED_FIGURES:
        if not (fig_dir / name).exists(): failures.append(f"missing retained figure: {name}")
    for name in ("fig11_computational_scaling.pdf", "fig11_computational_scaling.png"):
        if (fig_dir / name).exists(): failures.append("unsupported computational-scaling figure remains in authoritative figure set")
    if failures:
        print("PUBLICATION RELEASE AUDIT: FAIL"); [print(" -", f) for f in failures]; return 1

    tex = PAPER.read_text(encoding="utf-8"); bib = BIB.read_text(encoding="utf-8"); manifest = MANIFEST.read_text(encoding="utf-8"); release = RELEASE.read_text(encoding="utf-8")
    for pattern in EXPECTED:
        if not re.search(pattern, tex): failures.append(f"current validated aggregate missing from paper: {pattern}")
    for stale in STALE:
        if stale in tex: failures.append(f"stale numerical claim remains in paper: {stale}")
    if "results/independent_validation_run" in tex: failures.append("paper still references legacy independent_validation_run result authority")
    if "results/independent_validation_run" in release: failures.append("release document still names legacy independent_validation_run as current")
    if "results/authoritative_validation_20260815" not in tex: failures.append("paper does not reference the authoritative result package")
    if "authoritative_validation_20260815" not in manifest: failures.append("figure manifest is not sourced from the authoritative package")
    cited_groups = re.findall(r"\\cite(?:t|p)?\{([^}]+)\}", tex); keys = set(re.findall(r"^\s*@\w+\{\s*([^,]+),", bib, flags=re.MULTILINE))
    missing = sorted(k.strip() for group in cited_groups for k in group.split(",") if k.strip() not in keys)
    if missing: failures.append("missing bibliography keys: " + ", ".join(sorted(set(missing))))
    for phrase in ("load-shift", "stealth-drift", "field SCADA data"):
        if phrase not in tex: failures.append(f"required limitation statement missing: {phrase}")
    if "fig11_computational_scaling" in manifest or "fig11_computational_scaling" in release: failures.append("unsupported timing figure is still claimed in release documentation")
    if failures:
        print("PUBLICATION RELEASE AUDIT: FAIL"); [print(" -", f) for f in failures]; return 1
    print("PUBLICATION RELEASE AUDIT: PASS")
    print(" - one authoritative result package")
    print(" - retained publication figures present")
    print(" - stale numerical/speedup claims absent")
    print(" - bibliography resolved")
    print(" - benchmark/synthetic-data limitations explicit")
    return 0

if __name__ == "__main__": sys.exit(main())
