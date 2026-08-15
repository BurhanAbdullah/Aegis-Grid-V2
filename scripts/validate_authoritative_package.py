#!/usr/bin/env python3
"""Independent release-package consistency checks for the current five-seed study."""
from pathlib import Path
import csv
import math
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "results" / "authoritative_validation_20260815"
DET = DATA / "metrics" / "detector_outputs.csv"
MULTI = DATA / "multi_seed_summary.csv"
PHYS = DATA / "physical_sanity.csv"


def rows(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    assert DET.exists() and MULTI.exists() and PHYS.exists()
    det = rows(DET); multi = rows(MULTI); phys = rows(PHYS)
    assert len(det) == 1200, len(det)
    assert {r["case"] for r in det} == {"case9", "case14", "case30", "case118"}
    assert {r["scenario"] for r in det} == {"baseline", "branch_outage", "fdia", "load_shift", "stealth_drift"}
    assert sum(int(r["y_true"]) == 0 for r in det) == 240
    assert sum(int(r["y_true"]) == 1 for r in det) == 960
    assert {int(r["seed"]) for r in det} == {2026}
    assert all(int(r["d_k1"]) == (int(r["votes"]) >= 1) for r in det)
    assert all(int(r["d_k2"]) == (int(r["votes"]) >= 2) for r in det)
    assert all(math.isfinite(float(r["nis"])) and float(r["nis"]) >= 0 for r in det)
    assert all(0.0 <= float(r["s_comp"]) <= 1.0 for r in det)
    assert [int(r["seed"]) for r in multi] == [2026, 2027, 2028, 2029, 2030]
    f1 = np.array([float(r["F1"]) for r in multi]); rec = np.array([float(r["Recall"]) for r in multi]); fpr = np.array([float(r["FPR"]) for r in multi]); mcc = np.array([float(r["MCC"]) for r in multi])
    checks = {"F1": (f1.mean(), 0.9204), "Recall": (rec.mean(), 0.8850), "FPR": (fpr.mean(), 0.1525), "MCC": (mcc.mean(), 0.6667)}
    for name, (actual, expected) in checks.items(): assert abs(actual - expected) < 5e-4, (name, actual, expected)
    assert all(str(r["converged"]).lower() == "true" for r in phys)
    assert max(float(r["h_q_max_abs_error"]) for r in phys) < 1e-10
    assert max(abs(float(r["power_balance_residual"])) for r in phys) < 1e-9
    print("AUTHORITATIVE PACKAGE VALIDATION: PASS")
    print(f"rows={len(det)} seeds={len(multi)} physical_cases={len(phys)}")
    print(f"F1={f1.mean():.6f} Recall={rec.mean():.6f} FPR={fpr.mean():.6f} MCC={mcc.mean():.6f}")

if __name__ == "__main__":
    main()
