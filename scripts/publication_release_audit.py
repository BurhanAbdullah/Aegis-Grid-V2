#!/usr/bin/env python3
"""Conservative publication-release audit for the corrected XMON-Grid paper."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "main.tex"
BIB = ROOT / "paper" / "references.bib"
MANIFEST = ROOT / "results" / "independent_validation_run" / "paper_figures" / "FIGURE_MANIFEST.md"
RELEASE = ROOT / "RELEASE_20260814.md"
FIG_DIR = ROOT / "results" / "independent_validation_run" / "paper_figures"
REQUIRED = [PAPER, BIB, MANIFEST, RELEASE, ROOT / "results" / "independent_validation_run" / "tables" / "multi_seed_summary.csv"]

EXPECTED = {
    "F1": r"0\.9204\\pm0\.0026",
    "Recall": r"0\.8850\\pm0\.0012",
    "FPR": r"0\.1525\\pm0\.0197",
    "MCC": r"0\.6667\\pm0\.0151",
}

STALE = [
    r"0.9232\pm0.0032",
    r"0.8585\pm0.0048",
    r"0.0058\pm0.0073",
    "192.58",
]

REQUIRED_FIGURES = [
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
    for path in REQUIRED:
        if not path.exists():
            failures.append(f"missing required publication file: {path.relative_to(ROOT)}")

    for filename in REQUIRED_FIGURES:
        if not (FIG_DIR / filename).exists():
            failures.append(f"missing retained publication figure: {filename}")

    if (FIG_DIR / "fig11_computational_scaling.pdf").exists() or (FIG_DIR / "fig11_computational_scaling.png").exists():
        failures.append("unsupported computational-scaling figure is still present in publication figure set")

    if not PAPER.exists() or not BIB.exists() or not MANIFEST.exists() or not RELEASE.exists():
        print("PUBLICATION RELEASE AUDIT: FAIL")
        for failure in failures:
            print(" -", failure)
        return 1

    tex = PAPER.read_text(encoding="utf-8")
    bib = BIB.read_text(encoding="utf-8")
    manifest = MANIFEST.read_text(encoding="utf-8")
    release = RELEASE.read_text(encoding="utf-8")

    for label, pattern in EXPECTED.items():
        if not re.search(pattern, tex):
            failures.append(f"current {label} value not found in paper")

    for stale in STALE:
        if stale in tex:
            failures.append(f"stale numerical claim remains in paper: {stale}")

    cited_groups = re.findall(r"\\cite(?:t|p)?\{([^}]+)\}", tex)
    keys = set(re.findall(r"^\s*@\w+\{\s*([^,]+),", bib, flags=re.MULTILINE))
    missing = sorted(k.strip() for group in cited_groups for k in group.split(",") if k.strip() not in keys)
    if missing:
        failures.append("missing bibliography keys: " + ", ".join(sorted(set(missing))))

    for phrase in ("load-shift", "stealth-drift", "field SCADA data"):
        if phrase not in tex:
            failures.append(f"required limitation statement missing: {phrase}")

    if "fig11_computational_scaling" in manifest or "fig11_computational_scaling" in release:
        failures.append("unsupported computational-scaling figure is still claimed in release documentation")

    if failures:
        print("PUBLICATION RELEASE AUDIT: FAIL")
        for failure in failures:
            print(" -", failure)
        return 1

    print("PUBLICATION RELEASE AUDIT: PASS")
    print(" - current validated aggregate values present")
    print(" - known stale aggregate/speedup claims absent")
    print(" - bibliography citation keys resolved")
    print(" - retained publication figures present")
    print(" - unsupported timing figure excluded")
    print(" - release documentation present")
    print(" - principal limitations explicitly reported")
    return 0


if __name__ == "__main__":
    sys.exit(main())
