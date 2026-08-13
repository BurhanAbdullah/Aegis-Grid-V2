#!/usr/bin/env python3
"""Run the physical experiment without generating paper figures.

Figures are intentionally a separate post-gate step. This script creates the
raw/metric/table artifacts and a cryptographic manifest of those artifacts.
"""
import os
import sys
from scripts.run_authoritative_experiment import (
    SEED, DEFAULT_OUTPUT_DIR, run_experiment, generate_tables,
    independent_verification, generate_sha256sums,
)

out = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUTPUT_DIR
rows, _ = run_experiment(SEED, out)
roc, pr = generate_tables(rows, out)
metrics = independent_verification(os.path.join(out, "metrics", "detector_outputs.csv"))
generate_sha256sums(out)
print(f"VERIFIED-PIPELINE INPUT ARTIFACTS READY | ROC-AUC={roc:.6f} PR-AUC={pr:.6f} K2-F1={metrics['F1']:.6f}")
