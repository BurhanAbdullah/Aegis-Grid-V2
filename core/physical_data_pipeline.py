#!/usr/bin/env python3
"""Canonical AC power-flow-backed data generation for XMON-Grid.

Every sample is generated from a solved AC operating point. Attacks modify the
physical network or measurement equation explicitly; arbitrary synthetic
measurement offsets are not used for the FDIA case.
"""

import copy
import importlib
from typing import Dict, Tuple

import numpy as np
from pypower.api import runpf, ppoption
from pypower.idx_bus import PD, QD, VM, VA
from pypower.idx_brch import BR_STATUS
from pypower.makeYbus import makeYbus

from core.grid_topology import compute_h_x, compute_jacobian_H

SEVERITY_TIERS = ("Tier 1 (Subtle)", "Tier 2 (Moderate)", "Tier 3 (Strong)", "Tier 4 (Severe)")
SCENARIOS = ("baseline", "branch_outage", "fdia", "load_shift", "stealth_drift")
_CASE_CACHE: Dict[str, Dict] = {}
_OUTAGE_CACHE: Dict[str, Dict] = {}


def load_canonical_case(case_name: str) -> Dict:
    if case_name not in _CASE_CACHE:
        mod = importlib.import_module(f"pypower.{case_name}")
        _CASE_CACHE[case_name] = getattr(mod, case_name)()
    return copy.deepcopy(_CASE_CACHE[case_name])


def solve(ppc: Dict) -> Tuple[Dict, bool]:
    opts = ppoption(VERBOSE=0, OUT_ALL=0, PF_ALG=1, ENFORCE_Q_LIMS=0)
    return runpf(copy.deepcopy(ppc), opts)


def _dense_ybus(result: Dict) -> np.ndarray:
    ybus, _, _ = makeYbus(result["baseMVA"], result["bus"], result["branch"])
    return ybus.toarray() if hasattr(ybus, "toarray") else np.asarray(ybus, dtype=complex)


def _state_and_ybus(result: Dict) -> Tuple[np.ndarray, np.ndarray]:
    vm = result["bus"][:, VM]
    va = np.deg2rad(result["bus"][:, VA])
    return np.r_[va[1:], vm], _dense_ybus(result)


def solved_case(case_name: str) -> Tuple[Dict, np.ndarray, np.ndarray]:
    result, ok = solve(load_canonical_case(case_name))
    if not ok:
        raise RuntimeError(f"{case_name}: canonical Newton power flow failed")
    x, ybus = _state_and_ybus(result)
    return result, x, ybus


def _noise(rng: np.random.RandomState, n: int) -> np.ndarray:
    return np.r_[rng.normal(0.0, 0.002, n), rng.normal(0.0, 0.005, 2 * n)]


def _perturb_loads(ppc: Dict, rng: np.random.RandomState, multiplier: float) -> Dict:
    out = copy.deepcopy(ppc)
    pd = out["bus"][:, PD].copy(); qd = out["bus"][:, QD].copy()
    factors = multiplier * rng.normal(1.0, 0.015, len(pd))
    out["bus"][:, PD] = np.maximum(0.0, pd * factors)
    out["bus"][:, QD] = np.maximum(0.0, qd * factors)
    return out


def _branch_outage_case(case_name: str) -> Dict:
    if case_name in _OUTAGE_CACHE:
        return copy.deepcopy(_OUTAGE_CACHE[case_name])
    ppc = load_canonical_case(case_name)
    active = np.where(ppc["branch"][:, BR_STATUS] != 0)[0]
    for idx in active:
        candidate = copy.deepcopy(ppc)
        candidate["branch"][idx, BR_STATUS] = 0
        result, ok = solve(candidate)
        if ok and np.all(np.isfinite(result["bus"][:, VM])):
            _OUTAGE_CACHE[case_name] = candidate
            return copy.deepcopy(candidate)
    raise RuntimeError(f"{case_name}: no convergent single-branch outage found")


def _tier_sigma(tier: str) -> float:
    return {SEVERITY_TIERS[0]: 1.5, SEVERITY_TIERS[1]: 4.0,
            SEVERITY_TIERS[2]: 7.5, SEVERITY_TIERS[3]: 12.0}[tier]


def generate_sample(case_name: str, scenario: str, tier: str, sample_idx: int,
                    rng: np.random.RandomState) -> Tuple[np.ndarray, float, Dict]:
    base = load_canonical_case(case_name)
    n = base["bus"].shape[0]

    if scenario == "baseline":
        ppc = _perturb_loads(base, rng, 1.0); magnitude = 0.0; mode = "none"
    elif scenario == "branch_outage":
        ppc = _perturb_loads(_branch_outage_case(case_name), rng, 1.0 + 0.002 * (sample_idx % 4))
        magnitude = 1.0; mode = "physical_branch_outage"
    elif scenario == "load_shift":
        frac = {SEVERITY_TIERS[0]: 0.01, SEVERITY_TIERS[1]: 0.025,
                SEVERITY_TIERS[2]: 0.05, SEVERITY_TIERS[3]: 0.10}[tier]
        ppc = _perturb_loads(base, rng, 1.0 + frac); magnitude = frac; mode = "physical_load_shift"
    elif scenario == "stealth_drift":
        frac = 0.002 + 0.0005 * sample_idx
        ppc = _perturb_loads(base, rng, 1.0 + frac); magnitude = frac; mode = "physical_load_drift"
    elif scenario == "fdia":
        ppc = _perturb_loads(base, rng, 1.0); magnitude = _tier_sigma(tier); mode = "jacobian_fdia"
    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    result, ok = solve(ppc)
    if not ok:
        raise RuntimeError(f"{case_name}/{scenario}/{sample_idx}: AC Newton power flow failed")
    x, ybus = _state_and_ybus(result)
    h = compute_h_x(x, ybus.real, ybus.imag)
    z = h + _noise(rng, n)

    if scenario == "fdia":
        H = compute_jacobian_H(x, ybus.real, ybus.imag)
        c = np.zeros(2 * n - 1)
        support = rng.choice(len(c), size=max(2, min(5, len(c))), replace=False)
        c[support] = rng.normal(0.5, 0.2, len(support))
        direction = H @ c
        sigma = np.r_[np.full(n, 0.002), np.full(2 * n, 0.005)]
        peak = np.max(np.abs(direction) / sigma)
        if peak <= 1e-12:
            raise RuntimeError("Degenerate FDIA direction")
        z = z + direction * (_tier_sigma(tier) / peak)

    # Timing noise is deliberately independent of attack labels.
    delta_t = max(1e-4, float(rng.normal(0.004, 0.0005)))
    if rng.rand() < 0.20:
        delta_t = max(1e-4, float(rng.normal(0.006, 0.0015)))

    return z, delta_t, {
        "scenario": scenario,
        "severity_tier": "Tier 0 (Benign)" if scenario == "baseline" else tier,
        "attack_magnitude": round(float(magnitude), 8),
        "snr_estimate": round(float(magnitude), 4),
        "attack_mode": mode,
    }


def generate_physical_dataset(case_name: str, num_calibration: int = 200,
                               num_validation: int = 100, num_test_per_scenario: int = 60,
                               seed: int = 42) -> Dict:
    """Create strict benign-calibration, validation and untouched test splits."""
    rng = np.random.RandomState(seed)
    calibration_z, calibration_iat = [], []
    for i in range(num_calibration):
        z, dt, _ = generate_sample(case_name, "baseline", "Tier 0 (Benign)", i, rng)
        calibration_z.append(z); calibration_iat.append(dt)

    val_z, val_iat, val_labels = [], [], []
    for i in range(num_validation // 2):
        z, dt, _ = generate_sample(case_name, "baseline", "Tier 0 (Benign)", i, rng)
        val_z.append(z); val_iat.append(dt); val_labels.append(0)
    attacks = ("branch_outage", "fdia", "load_shift", "stealth_drift")
    for i in range(num_validation // 2):
        sc, tier = attacks[i % 4], SEVERITY_TIERS[i % 4]
        z, dt, _ = generate_sample(case_name, sc, tier, i, rng)
        val_z.append(z); val_iat.append(dt); val_labels.append(1)

    test_z, test_iat, test_labels, metadata = [], [], [], []
    for scenario in SCENARIOS:
        for i in range(num_test_per_scenario):
            tier = "Tier 0 (Benign)" if scenario == "baseline" else SEVERITY_TIERS[i % 4]
            z, dt, meta = generate_sample(case_name, scenario, tier, i, rng)
            test_z.append(z); test_iat.append(dt); test_labels.append(0 if scenario == "baseline" else 1)
            metadata.append({"case": case_name, "sample_idx": i, **meta})

    return {
        "case_name": case_name,
        "calibration": {"z": np.asarray(calibration_z), "iat": np.asarray(calibration_iat)},
        "validation": {"z": np.asarray(val_z), "iat": np.asarray(val_iat), "labels": np.asarray(val_labels)},
        "test": {"z": np.asarray(test_z), "iat": np.asarray(test_iat), "labels": np.asarray(test_labels), "metadata": metadata},
    }
