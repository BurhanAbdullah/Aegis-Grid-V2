#!/usr/bin/env python3
"""
Grid topology and AC measurement equation engine for XMON-Grid.

The benchmark cases are loaded directly from the standard PYPOWER/MATPOWER
case definitions rather than synthetic approximations. This keeps the
benchmark topology and electrical parameters tied to a versioned definition.
"""

from importlib import import_module
from typing import Dict, Tuple, Any

import numpy as np

_CASE_MODULES = {
    "case9": "pypower.case9",
    "case14": "pypower.case14",
    "case30": "pypower.case30",
    "case118": "pypower.case118",
}


def get_ieee_case_data(case_name: str) -> Dict[str, Any]:
    """Return canonical IEEE benchmark data from PYPOWER case definitions."""
    case_name = case_name.lower().strip()
    if case_name not in _CASE_MODULES:
        raise ValueError(f"Unknown test case: {case_name}. Supported: {sorted(_CASE_MODULES)}")

    module = import_module(_CASE_MODULES[case_name])
    mpc = getattr(module, case_name)()
    bus = np.asarray(mpc["bus"], dtype=float)
    branch = np.asarray(mpc["branch"], dtype=float)
    base_mva = float(mpc["baseMVA"])

    if bus.ndim != 2 or bus.shape[1] < 13:
        raise ValueError(f"Invalid {case_name} bus matrix shape: {bus.shape}")
    if branch.ndim != 2 or branch.shape[1] < 13:
        raise ValueError(f"Invalid {case_name} branch matrix shape: {branch.shape}")

    return {
        "case_name": case_name,
        "source": "PYPOWER/MATPOWER standard case definition",
        "baseMVA": base_mva,
        "bus": bus,
        "branch": branch,
        "gen": np.asarray(mpc.get("gen", []), dtype=float),
        "gencost": np.asarray(mpc.get("gencost", []), dtype=float),
        "buses": bus.tolist(),
        "branches": branch.tolist(),
        "num_buses": int(bus.shape[0]),
        "num_branches": int(branch.shape[0]),
    }


def build_ybus(case_data: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Construct the MATPOWER-compatible bus admittance matrix."""
    bus = np.asarray(case_data["bus"], dtype=float)
    branch = np.asarray(case_data["branch"], dtype=float)
    base_mva = float(case_data["baseMVA"])
    n = int(case_data["num_buses"])

    ybus = np.zeros((n, n), dtype=complex)
    for row in bus:
        i = int(round(row[0])) - 1
        if not 0 <= i < n:
            raise ValueError(f"Invalid bus number {row[0]}")
        ybus[i, i] += complex(row[4], row[5]) / base_mva

    for row in branch:
        if row[10] == 0:
            continue
        f = int(round(row[0])) - 1
        t = int(round(row[1])) - 1
        if not (0 <= f < n and 0 <= t < n):
            raise ValueError(f"Invalid branch endpoints {row[0]} -> {row[1]}")

        z = complex(row[2], row[3])
        if abs(z) <= 1e-15:
            raise ValueError(f"Zero branch impedance on {row[0]} -> {row[1]}")
        y = 1.0 / z
        b_shunt = complex(0.0, row[4])
        ratio = float(row[8]) or 1.0
        shift = np.deg2rad(float(row[9]))
        tap = ratio * np.exp(1j * shift)

        yff = (y + b_shunt / 2.0) / (tap * np.conj(tap))
        yft = -y / np.conj(tap)
        ytf = -y / tap
        ytt = y + b_shunt / 2.0
        ybus[f, f] += yff
        ybus[f, t] += yft
        ybus[t, f] += ytf
        ybus[t, t] += ytt

    return ybus, ybus.real, ybus.imag


def compute_h_x(x: np.ndarray, G: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Evaluate h(x)=[V,P,Q], with reference-bus angle fixed at zero."""
    n = G.shape[0]
    x = np.asarray(x, dtype=float)
    if x.size != 2 * n - 1:
        raise ValueError(f"State dimension mismatch: expected {2*n-1}, got {x.size}")

    theta = np.zeros(n)
    theta[1:] = x[: n - 1]
    v = x[n - 1 :]
    d_ij = theta[:, None] - theta[None, :]
    cos_d = np.cos(d_ij)
    sin_d = np.sin(d_ij)

    p = v * np.sum(v[None, :] * (G * cos_d + B * sin_d), axis=1)
    q = v * np.sum(v[None, :] * (G * sin_d - B * cos_d), axis=1)
    return np.concatenate([v, p, q])


def compute_jacobian_H(x: np.ndarray, G: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Evaluate the exact analytical Jacobian H=dh/dx."""
    n = G.shape[0]
    x = np.asarray(x, dtype=float)
    if x.size != 2 * n - 1:
        raise ValueError(f"State dimension mismatch: expected {2*n-1}, got {x.size}")

    theta = np.zeros(n)
    theta[1:] = x[: n - 1]
    v = x[n - 1 :]
    d_ij = theta[:, None] - theta[None, :]
    cos_d = np.cos(d_ij)
    sin_d = np.sin(d_ij)
    vv = v[:, None] * v[None, :]

    hp_theta_full = vv * (G * sin_d - B * cos_d)
    np.fill_diagonal(hp_theta_full, 0.0)
    np.fill_diagonal(hp_theta_full, -np.sum(hp_theta_full, axis=1))

    hq_theta_full = -vv * (G * cos_d + B * sin_d)
    np.fill_diagonal(hq_theta_full, 0.0)
    np.fill_diagonal(hq_theta_full, -np.sum(hq_theta_full, axis=1))

    hp_v = v[:, None] * (G * cos_d + B * sin_d)
    np.fill_diagonal(hp_v, 0.0)
    np.fill_diagonal(hp_v, 2.0 * v * np.diag(G) + np.sum(hp_v, axis=1))

    hq_v = v[:, None] * (G * sin_d - B * cos_d)
    np.fill_diagonal(hq_v, 0.0)
    np.fill_diagonal(hq_v, -2.0 * v * np.diag(B) + np.sum(hq_v, axis=1))

    h_v = np.hstack([np.zeros((n, n - 1)), np.eye(n)])
    h_p = np.hstack([hp_theta_full[:, 1:], hp_v])
    h_q = np.hstack([hq_theta_full[:, 1:], hq_v])
    return np.vstack([h_v, h_p, h_q])


# Backward-compatible name used by the validation scripts.
def compute_jacobian(x: np.ndarray, G: np.ndarray, B: np.ndarray) -> np.ndarray:
    return compute_jacobian_H(x, G, B)
