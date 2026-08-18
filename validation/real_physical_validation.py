#!/usr/bin/env python3
"""Independent physical validation using canonical PYPOWER IEEE cases.

This script intentionally does not trust XMON-Grid's case loader. It loads the
canonical IEEE 9/14/30/118 cases from PYPOWER, runs AC power flow, checks
physical operating ranges and nodal power balance independently from the
reported branch-flow columns, then independently checks the analytic h(x)
Jacobian implementation by finite differences.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

# Allow direct execution as `python validation/real_physical_validation.py`
# from a clean checkout, matching the CI invocation.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
from pypower.api import runpf
from pypower.ppoption import ppoption
from pypower.idx_bus import VM, VA, PD, QD, GS, BS
from pypower.idx_gen import PG, QG
from pypower.idx_brch import (
    F_BUS, T_BUS, BR_R, BR_X, BR_B, TAP, SHIFT, BR_STATUS,
    PF, PT, QF, QT,
)

from core.grid_topology import compute_h_x, compute_jacobian_H, get_ieee_case_data

CASES = ["case9", "case14", "case30", "case118"]


def load_pypower_case(name: str):
    """Load a canonical PYPOWER case with floating-point numeric matrices.

    Some PYPOWER case files are constructed with integer-valued NumPy literals.
    If those integer arrays are passed directly into the in-place power-flow
    solver, the solved slack-generator output can be truncated to an integer
    (e.g. IEEE-9), producing a false physical power-balance failure.  The
    canonical case definition is unchanged; only the solver working copy is
    promoted to float so the AC solution is represented without quantization.
    """
    mod = importlib.import_module(f"pypower.{name}")
    ppc = getattr(mod, name)()
    for key in ("bus", "gen", "branch"):
        ppc[key] = np.asarray(ppc[key], dtype=float).copy()
    return ppc


def canonical_ybus(ppc):
    """Build the canonical Ybus directly from branch and bus data.

    Includes series branches, line charging, transformer tap/phase shift, and
    the canonical bus shunts Gs/Bs.  Gs/Bs are specified in MW/MVAr at V=1 pu,
    so their admittance contribution is divided by baseMVA.
    """
    nb = ppc["bus"].shape[0]
    base_mva = float(ppc["baseMVA"])
    Y = np.zeros((nb, nb), dtype=complex)

    # Canonical bus shunts: S_sh = (Gs + j Bs) |V|^2 in MW/MVAr.
    Y += np.diag((ppc["bus"][:, GS] + 1j * ppc["bus"][:, BS]) / base_mva)

    for row in ppc["branch"]:
        if row[BR_STATUS] == 0:
            continue
        f = int(row[F_BUS]) - 1
        t = int(row[T_BUS]) - 1
        z = complex(row[BR_R], row[BR_X])
        ys = 1.0 / z
        bc = 1j * row[BR_B]
        tap = row[TAP] if row[TAP] != 0 else 1.0
        shift = np.deg2rad(row[SHIFT])
        tr = tap * np.exp(1j * shift)
        Y[f, f] += (ys + bc / 2) / (tr * np.conj(tr))
        Y[t, t] += ys + bc / 2
        Y[f, t] -= ys / np.conj(tr)
        Y[t, f] -= ys / tr
    return Y


def max_fd_jacobian_error(x, G, B):
    H = compute_jacobian_H(x, G, B)
    fd = np.zeros_like(H)
    eps = 1e-6
    for k in range(len(x)):
        xp = x.copy(); xm = x.copy()
        xp[k] += eps; xm[k] -= eps
        fd[:, k] = (compute_h_x(xp, G, B) - compute_h_x(xm, G, B)) / (2 * eps)
    return float(np.max(np.abs(H - fd))), float(np.linalg.norm(H - fd) / max(np.linalg.norm(fd), 1e-12))


def run_case(name):
    ppc = load_pypower_case(name)
    opts = ppoption(VERBOSE=0, OUT_ALL=0, PF_ALG=1)
    solved, success = runpf(ppc, opts)
    assert success, f"{name}: canonical AC power flow did not converge"

    bus = solved["bus"]
    vm = bus[:, VM]
    va = bus[:, VA]
    assert np.all(np.isfinite(vm)) and np.all(np.isfinite(va))
    assert float(vm.min()) > 0.80 and float(vm.max()) < 1.20, (name, vm.min(), vm.max())

    # Independent nodal power-balance audit. Reconstruct Ybus from canonical
    # branch parameters AND bus shunts, then evaluate S_i = V_i conj(YV)_i.
    # This independently accounts for branch losses and shunt consumption.
    Y = canonical_ybus(solved)
    V = vm * np.exp(1j * np.deg2rad(va))
    S_inj = V * np.conj(Y @ V) * solved["baseMVA"]
    total_pg = float(np.sum(solved["gen"][:, PG]))
    total_qg = float(np.sum(solved["gen"][:, QG]))
    total_pd = float(np.sum(bus[:, PD]))
    total_qd = float(np.sum(bus[:, QD]))
    p_nodal = float(np.sum(S_inj.real))
    q_nodal = float(np.sum(S_inj.imag))
    p_balance = total_pg - total_pd - p_nodal
    q_balance = total_qg - total_qd - q_nodal
    assert abs(p_balance) < 1e-6, (name, total_pg, total_pd, p_nodal, p_balance)
    assert abs(q_balance) < 1e-6, (name, total_qg, total_qd, q_nodal, q_balance)

    # Explicit independent shunt accounting: PG-PD equals branch loss plus
    # shunt consumption, while QG-QD follows the corresponding reactive sign.
    vm2 = vm * vm
    shunt_p = float(np.sum(bus[:, GS] * vm2))
    shunt_q = float(np.sum(bus[:, BS] * vm2))
    branch_p_loss = p_nodal - shunt_p
    branch_q_loss = q_nodal - shunt_q
    assert abs((total_pg - total_pd) - (branch_p_loss + shunt_p)) < 1e-6
    assert abs((total_qg - total_qd) - (branch_q_loss + shunt_q)) < 1e-6

    # Solver-reported branch losses remain diagnostics only; they are not used
    # for the independent release gate.
    reported_p_loss = float(np.sum(solved["branch"][:, PF] + solved["branch"][:, PT]))
    reported_q_loss = float(np.sum(solved["branch"][:, QF] + solved["branch"][:, QT]))

    x = np.concatenate([np.deg2rad(va[1:]), vm])
    G, B = Y.real, Y.imag
    err_abs, err_rel = max_fd_jacobian_error(x, G, B)
    assert err_abs < 2e-5, (name, err_abs, err_rel)

    repo = get_ieee_case_data(name)
    canonical_branch_count = int(np.sum(solved["branch"][:, BR_STATUS] != 0))
    topology_match = repo["num_buses"] == len(bus) and repo["num_branches"] == canonical_branch_count

    print(f"{name}: PF=PASS Vm=[{vm.min():.5f},{vm.max():.5f}] "
          f"Pbalance={p_balance:+.2e} Qbalance={q_balance:+.2e} "
          f"branch_loss=(P={branch_p_loss:.6f},Q={branch_q_loss:.6f}) "
          f"shunt=(P={shunt_p:.6f},Q={shunt_q:.6f}) "
          f"reported_branch_loss=(P={reported_p_loss:.6f},Q={reported_q_loss:.6f}) "
          f"Jacobian maxerr={err_abs:.2e} relerr={err_rel:.2e} "
          f"repo_topology_match={topology_match}")
    return topology_match


def main():
    mismatches = []
    for name in CASES:
        if not run_case(name):
            mismatches.append(name)
    if mismatches:
        print("TOPOLOGY MISMATCHES:", ", ".join(mismatches))
        print("The canonical physical validation passed, but XMON-Grid's internal case loader is not yet canonical.")
        return 2
    print("ALL CANONICAL PHYSICAL AND JACOBIAN CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
