#!/usr/bin/env python3
"""Independent canonical physical and Jacobian validation."""
import importlib
import sys
from pathlib import Path

import numpy as np
from pypower.api import runpf, ppoption
from pypower.idx_bus import VM, VA, PD, QD, GS, BS
from pypower.idx_gen import PG, QG
from pypower.idx_brch import F_BUS, T_BUS, BR_R, BR_X, BR_B, TAP, SHIFT, BR_STATUS, PF, QF, PT, QT

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.grid_topology import compute_h_x, compute_jacobian_H, get_ieee_case_data

CASES = ("case9", "case14", "case30", "case118")


def load_case(name):
    mod = importlib.import_module(f"pypower.{name}")
    return getattr(mod, name)()


def build_ybus(ppc):
    n = ppc["bus"].shape[0]
    Y = np.zeros((n, n), dtype=complex)
    for br in ppc["branch"]:
        if br[BR_STATUS] == 0:
            continue
        f, t = int(br[F_BUS])-1, int(br[T_BUS])-1
        ys = 1.0 / complex(br[BR_R], br[BR_X])
        ysh = 1j * br[BR_B] / 2.0
        tap = br[TAP] if abs(br[TAP]) > 1e-12 else 1.0
        tr = tap * np.exp(1j * np.deg2rad(br[SHIFT]))
        Y[f, f] += (ys+ysh)/(tr*np.conj(tr))
        Y[t, t] += ys+ysh
        Y[f, t] -= ys/np.conj(tr)
        Y[t, f] -= ys/tr
    return Y


def jacobian_error(x, G, B):
    H = compute_jacobian_H(x, G, B)
    eps = 1e-6
    fd = np.empty_like(H)
    for k in range(len(x)):
        xp = x.copy(); xm = x.copy(); xp[k] += eps; xm[k] -= eps
        fd[:, k] = (compute_h_x(xp, G, B)-compute_h_x(xm, G, B))/(2*eps)
    return float(np.max(np.abs(H-fd))), float(np.linalg.norm(H-fd)/np.linalg.norm(fd))


def check(name):
    ppc = load_case(name)
    result, ok = runpf(ppc, ppoption(VERBOSE=0, OUT_ALL=0, PF_ALG=1))
    assert ok, f"{name}: AC Newton power flow failed"
    bus, gen, br = result["bus"], result["gen"], result["branch"]
    vm = bus[:, VM]
    assert np.all(np.isfinite(vm)) and vm.min() > 0.80 and vm.max() < 1.20

    # Physical active/reactive balance in MW/MVAr. Include bus shunts explicitly.
    # KCL requires sum(Pg-Pd-Gs*V^2) = sum(branch P flows), and likewise for Q.
    p_gen = float(np.sum(gen[:, PG]))
    p_load = float(np.sum(bus[:, PD]))
    p_shunt = float(np.sum(bus[:, GS] * vm**2))
    p_branch_loss = float(np.sum(br[:, PF] + br[:, PT]))
    q_gen = float(np.sum(gen[:, QG]))
    q_load = float(np.sum(bus[:, QD]))
    q_shunt = float(np.sum(bus[:, BS] * vm**2))
    q_branch_loss = float(np.sum(br[:, QF] + br[:, QT]))
    p_bal_branch = p_gen - p_load - p_shunt - p_branch_loss
    q_bal_branch = q_gen - q_load - q_shunt - q_branch_loss

    # Independent network-equation check from V*conj(YV), in physical MW/MVAr.
    Y = build_ybus(result)
    Vc = vm * np.exp(1j*np.deg2rad(bus[:, VA]))
    s_net = Vc * np.conj(Y @ Vc) * float(result["baseMVA"])
    p_net = float(np.sum(s_net.real))
    q_net = float(np.sum(s_net.imag))
    p_bal_ybus = p_gen - p_load - p_shunt - p_net
    q_bal_ybus = q_gen - q_load - q_shunt - q_net

    print(
        f"{name}: totals Pg={p_gen:.9f} Pd={p_load:.9f} GsV2={p_shunt:.9f} "
        f"branchP={p_branch_loss:.9f} YbusP={p_net:.9f} | "
        f"Pbal_branch={p_bal_branch:+.9e} Pbal_ybus={p_bal_ybus:+.9e}"
    )
    print(
        f"{name}: totals Qg={q_gen:.9f} Qd={q_load:.9f} BsV2={q_shunt:.9f} "
        f"branchQ={q_branch_loss:.9f} YbusQ={q_net:.9f} | "
        f"Qbal_branch={q_bal_branch:+.9e} Qbal_ybus={q_bal_ybus:+.9e}"
    )

    assert abs(p_bal_branch) < 1e-6, f"{name}: P branch balance {p_bal_branch}"
    assert abs(q_bal_branch) < 1e-6, f"{name}: Q branch balance {q_bal_branch}"
    assert abs(p_bal_ybus) < 1e-6, f"{name}: P Ybus balance {p_bal_ybus}"
    assert abs(q_bal_ybus) < 1e-6, f"{name}: Q Ybus balance {q_bal_ybus}"

    x = np.r_[np.deg2rad(bus[1:, VA]), vm]
    emax, erel = jacobian_error(x, Y.real, Y.imag)
    assert emax < 2e-5, f"{name}: Jacobian error {emax}"
    repo = get_ieee_case_data(name)
    active = int(np.sum(br[:, BR_STATUS] != 0))
    assert repo["num_buses"] == len(bus) and repo["num_branches"] == active, f"{name}: topology mismatch"
    print(f"{name}: PASS | buses={len(bus)} branches={active} Vm=[{vm.min():.5f},{vm.max():.5f}] Jmax={emax:.2e} Jrel={erel:.2e}")


if __name__ == "__main__":
    for c in CASES:
        check(c)
    print("ALL CANONICAL PHYSICAL/JACOBIAN CHECKS PASSED")
