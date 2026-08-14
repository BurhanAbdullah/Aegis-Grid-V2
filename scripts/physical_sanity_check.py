#!/usr/bin/env python3
"""Independent physical consistency audit of the canonical AC network model."""
from pathlib import Path
import sys
import csv
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core.grid_topology import get_ieee_case_data, build_ybus, compute_h_x


def solve_state(case_name):
    from pypower.api import ppoption, runpf
    module = __import__(f"pypower.{case_name}", fromlist=[case_name])
    mpc = getattr(module, case_name)()
    solved, success = runpf(mpc, ppoption(VERBOSE=0, OUT_ALL=0))
    if not success:
        raise RuntimeError(f"AC power flow failed for {case_name}")
    bus = np.asarray(solved["bus"], dtype=float)
    va = np.deg2rad(bus[:, 8]); vm = bus[:, 7]
    return np.concatenate([va[1:], vm]), vm*np.exp(1j*va)


def audit_case(case_name):
    case = get_ieee_case_data(case_name)
    _, G, B = build_ybus(case)
    x, V = solve_state(case_name)
    Ybus, _, _ = build_ybus(case)
    S_bus = V * np.conj(Ybus @ V)
    h = compute_h_x(x, G, B)
    n = case["num_buses"]
    h_p_err = float(np.max(np.abs(h[n:2*n] - S_bus.real)))
    h_q_err = float(np.max(np.abs(h[2*n:] - S_bus.imag)))

    bus = np.asarray(case["bus"], dtype=float)
    p_shunt = float(np.sum(bus[:, 4] / case["baseMVA"] * np.abs(V)**2))
    p_branch_loss = 0.0
    for row in np.asarray(case["branch"], dtype=float):
        if row[10] == 0:
            continue
        f, t = int(row[0]) - 1, int(row[1]) - 1
        y = 1.0 / complex(row[2], row[3])
        ratio = float(row[8]) or 1.0
        tap = ratio * np.exp(1j*np.deg2rad(float(row[9])))
        Ift = (V[f] / tap - V[t]) * y
        Itf = (V[t] - V[f] / tap) * y
        p_branch_loss += float(np.real((V[f] / tap) * np.conj(Ift) + V[t] * np.conj(Itf)))
    residual = float(np.sum(S_bus.real) - p_branch_loss - p_shunt)
    return {"case": case_name, "buses": n, "branches": case["num_branches"],
            "h_p_max_abs_error": h_p_err, "h_q_max_abs_error": h_q_err,
            "power_balance_residual": residual, "converged": True}


def main():
    rows = [audit_case(c) for c in ("case9", "case14", "case30", "case118")]
    for r in rows:
        msg = (f"{r['case']}: hP={r['h_p_max_abs_error']:.3e}, "
               f"hQ={r['h_q_max_abs_error']:.3e}, "
               f"balance={r['power_balance_residual']:.3e}")
        print(msg)
        if r["h_p_max_abs_error"] > 1e-10 or r["h_q_max_abs_error"] > 1e-10 or abs(r["power_balance_residual"]) > 1e-9:
            raise SystemExit(f"PHYSICAL SANITY CHECK FAILED: {r['case']}")
    out = ROOT / "results" / "current_physical_sanity.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader(); writer.writerows(rows)
    print("PHYSICAL MODEL SANITY CHECK: PASS")


if __name__ == "__main__":
    main()
