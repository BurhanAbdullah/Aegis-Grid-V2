#!/usr/bin/env python3
"""Fail-fast checks for claims that must agree with the current implementation."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
PAPER = (ROOT / "paper" / "main.tex").read_text(encoding="utf-8")
PIPELINE = (ROOT / "core" / "data_pipeline.py").read_text(encoding="utf-8")

failures = []

for name, text in (("README", README), ("paper", PAPER)):
    for forbidden in ("pandapower", "PyPSA", "8.25\\times", "192.58\\times", "8.25×", "192.58×"):
        if forbidden in text:
            failures.append(f"{name}: unsupported claim/dependency remains: {forbidden}")

if "canonical PYPOWER IEEE topology; synthetic seeded measurements/attacks" not in PIPELINE:
    failures.append("pipeline: benchmark provenance marker missing")

if "pypower==5.1.19" not in (ROOT / "requirements.txt").read_text(encoding="utf-8"):
    failures.append("requirements: pinned PYPOWER dependency missing")

if not (ROOT / ".gitmodules").exists():
    failures.append("repository: .gitmodules missing while matpower is a gitlink")

if failures:
    print("REPRODUCIBILITY CONTRACT: FAIL")
    for failure in failures:
        print(f" - {failure}")
    raise SystemExit(1)

print("REPRODUCIBILITY CONTRACT: PASS")
print("Current manuscript/repository claims are consistent with the canonical PYPOWER + synthetic benchmark implementation.")
