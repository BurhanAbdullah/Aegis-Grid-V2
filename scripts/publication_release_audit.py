#!/usr/bin/env python3
"""Publication-release audit for the corrected XMON-Grid manuscript.

This audit is deliberately conservative: it checks that the manuscript contains
only the current validated aggregate values, rejects known stale claims, checks
that cited reference keys exist, and verifies the required publication files.
It does not manufacture or overwrite scientific results.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper" / "main.tex"
BIB = ROOT / "paper" / "references.bib"
REQUIRED = [PAPER, BIB, ROOT / "results" / "independent_validation_run" / "tables" / "multi_seed_summary.csv"]

EXPECTED = {
    "F1": r"0\.9204\\pm0\.0026",
    "Recall": r"0\.8850\\pm0\.0012",
    "FPR": r"0\.1525\\pm0\.0197",
    "MCC": r"0\.6667\\pm0\.0151",
}

STALE = [
    "0.9232\\\\pm0.0032",
    "0.8585\\\\pm0.0048",
    "0.0058\\\\pm0.0073",
    "192.58",
    "192.58×",
]


def main() -> int:
    failures = []
    for path in REQUIRED:
        if not path.exists():
            failures.append(f"missing required publication file: {path.relative_to(ROOT)}")

    if not PAPER.exists() or not BIB.exists():
        for item in failures:
            print("FAIL:", item)
        return 1

    tex = PAPER.read_text(encoding="utf-8")
    bib = BIB.read_text(encoding="utf-8")

    for label, pattern in EXPECTED.items():
        if not re.search(pattern, tex):
            failures.append(f"current {label} value not found in paper")

    for stale in STALE:
        if stale in tex:
            failures.append(f"stale numerical claim remains in paper: {stale}")

    # Every bibliography citation key used by the manuscript must be defined.
    cited = set(re.findall(r"\\cite(?:t|p)?\{([^}]+)\}", tex))
    keys = set(re.findall(r"^\s*@\w+\{\s*([^,]+),", bib, flags=re.MULTILINE))
    missing = sorted(k for group in cited for k in group.split(",") if k.strip() not in keys)
    if missing:
        failures.append("missing bibliography keys: " + ", ".join(sorted(set(missing))))

    # The manuscript must explicitly acknowledge the two main limitations.
    for phrase in ("load-shift", "stealth-drift", "field SCADA data"):
        if phrase not in tex:
            failures.append(f"required limitation statement missing: {phrase}")

    if failures:
        print("PUBLICATION RELEASE AUDIT: FAIL")
        for failure in failures:
            print(" -", failure)
        return 1

    print("PUBLICATION RELEASE AUDIT: PASS")
    print(" - current validated aggregate values present")
    print(" - known stale aggregate/speedup claims absent")
    print(" - bibliography citation keys resolved")
    print(" - required publication artifacts present")
    print(" - principal limitations explicitly reported")
    return 0


if __name__ == "__main__":
    sys.exit(main())
