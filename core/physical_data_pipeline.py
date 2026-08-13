#!/usr/bin/env python3
"""Canonical AC power-flow-backed data generation for XMON-Grid.

This module deliberately separates the physical plant model from the detector:
1. load a canonical PYPOWER IEEE case;
2. perturb operating conditions and solve an AC Newton power flow;
3. map the solved state into XMON's measurement vector h(x);
4. add documented Gaussian measurement noise;
5. inject attacks in physically meaningful ways.

The FDIA implementation uses a=Hc at the solved operating point rather than
arbitrary additive P/Q offsets. Branch outages and load shifts modify the
network operating point before measurements are generated.
"""

import copy
import importlib
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
from pypower.api import runpf, ppoption
from pypower.idx_bus import PD, QD, VM, VA
from pypower.idx_brch import BR_STATUS
from pypower.makeYbus import makeYbus

from core.grid_topology import compute_h_x, compute_jacobian_H

SEVERITY_TIERS = (
    "Tier 1 (Subtle)",
    "Tier 2 (Moderate)",
    "Tier 3 (Strong)",
    "Tier 4 (Severe)",
)
SCENARIOS = ("baseline", "branch_outage", "fdia", "load_shift", "stealth_drift")

@dataclass
class PhysicalCase:
    name: str
    ppc: Dict
    ybus: np.ndarray
    x: np.ndarray


def load_canonical_case(case_name: str) -> Dict:
    """Return an unmodified canonical PYPOWER case."""
    mod = importlib.import_module(f"pypower.{case_name}")
    return getattr(mod, case_name)()


def solve(ppc: Dict) -> Tuple[Dict, bool]:
    """Run a quiet Newton AC power flow and return (result, converged)."""
    opts = ppoption(VERBOSE=0, OUT_ALL=0, PF_ALG=1, ENFORCE_Q_LIMS=0)
    return runpf(copy.deepcopy(ppc), opts)


def solved_case(case_name: str) -> PhysicalCase:
    ppc = load_canonical_case(case_name)
    result, ok = solve(ppc)
    if not ok:
        raise RuntimeError(f"{case_name}: canonical Newton power flow did not converge")
    ybus, _, _ = makeYbus(result["baseMVA"], result["bus"], result["branch"])
    vm = result["bus"][:, VM]
    va = np.deg2rad(result["bus"][:, VA])
    x = np.r_[va[1:], vm]
    return PhysicalCase(case_name, result, np.asarray(ybus), x)


def _state_and_ybus(result: Dict) -> Tuple[np.ndarray, np.ndarray]:
    ybus, _, _ = makeYbus(result["baseMVA"], result["bus"], result["branch"])
    vm = result["bus"][:, VM]
    va = np.deg2rad(result["bus"][:, VA])
    return np.r_[va[1:], vm], np.asarray(ybus)


def _noise(rng: np.random.RandomState, n: int) -> np.ndarray:
    return np.r_[rng.normal(0.0, 0.002, n),
                 rng.normal(0.0, 0.005, 2 * n)]


def _perturb_loads(ppc: Dict, rng: np.random.RandomState, multiplier: float) -> Dict:
    out = copy.deepcopy(ppc)
    base_pd = out["bus"][:, PD].copy()
    base_qd = out["bus"][:, QD].copy()
    # Only perturb nonzero loads; keep the operating point physically meaningful.
    factors = multiplier * rng.normal(1.0, 0.015, len(base_pd))
    out["bus"][:, PD] = np.maximum(0.0, base_pd * factors)
    out["bus"][:, QD] = np.maximum(0.0, base_qd * factors)
    return out


def _branch_outage_case(ppc: Dict) -> Dict:
    out = copy.deepcopy(ppc)
    active = np.where(out["branch"][:, BR_STATUS] != 0)[0]
    if len(active) == 0:
        raise RuntimeError("No active branch available for outage experiment")
    # Select the first active branch and require the resulting power flow to converge.
    for idx in active:
        candidate = copy.deepcopy(ppc)
        candidate["branch"][idx, BR_STATUS] = 0
        result, ok = solve(candidate)
        if ok and np.all(np.isfinite(result["bus"][:, VM])):
            return candidate
    raise RuntimeError("No single-branch outage converged for this case")


def _tier_sigma(tier: str) -> float:
    return {SEVERITY_TIERS[0]: 1.5, SEVERITY_TIERS[1]: 4.0,
            SEVERITY_TIERS[2]: 7.5, SEVERITY_TIERS[3]: 12.0}[tier]


def generate_sample(case_name: str, scenario: str, tier: str,
                    sample_idx: int, rng: np.random.RandomState) -> Tuple[np.ndarray, float, Dict]:
    """Generate one physically grounded measurement sample."""
    base = load_canonical_case(case_name)
    n = base["bus"].shape[0]

    if scenario == "baseline":
        ppc = _perturb_loads(base, rng, 1.0)
        attack_magnitude = 0.0
        attack_mode = "none"
    elif scenario == "branch_outage":
        ppc = _branch_outage_case(base)
        ppc = _perturb_loads(ppc, rng, 1.0 + 0.002 * (sample_idx % 4))
        attack_magnitude = 1.0
        attack_mode = "physical_branch_outage"
    elif scenario == "load_shift":
        frac = {SEVERITY_TIERS[0]: 0.01, SEVERITY_TIERS[1]: 0.025,
                SEVERITY_TIERS[2]: 0.05, SEVERITY_TIERS[3]: 0.10}[tier]
        ppc = _perturb_loads(base, rng, 1.0 + frac)
        attack_magnitude = frac
        attack_mode = "physical_load_shift"
    elif scenario == "stealth_drift":
        # A trajectory is represented by a deterministic operating-point drift.
        frac = 0.002 + 0.0005 * sample_idx
        ppc = _perturb_loads(base, rng, 1.0 + frac)
        attack_magnitude = frac
        attack_mode = "physical_load_drift"
    elif scenario == "fdia":
        ppc = _perturb_loads(base, rng, 1.0)
        attack_magnitude = _tier_sigma(tier)
        attack_mode = "jacobian_nullspace_fdia"
    else:
        raise ValueError(f"Unknown scenario: {scenario}")

    result, ok = solve(ppc)
    if not ok:
        raise RuntimeError(f"{case_name}/{scenario}/{sample_idx}: AC power flow failed")
    x, ybus = _state_and_ybus(result)
    h = compute_h_x(x, ybus.real, ybus.imag)
    z = h + _noise(rng, n)

    # Canonical stealth FDIA: a = H(x)c, scaled to the requested sigma level.
    if scenario == "fdia":
        H = compute_jacobian_H(x, ybus.real, ybus.imag)
        c = np.zeros(2 * n - 1)
        support = rng.choice(len(c), size=max(2, min(5, len(c))), replace=False)
        c[support] = rng.normal(0.5, 0.2, len(support))
        direction = H @ c
        sigma = np.r_[np.full(n, 0.002), np.full(2 * n, 0.005)]
        normalized_peak = np.max(np.abs(direction) / sigma)
        if normalized_peak <= 1e-12:
            raise RuntimeError("Degenerate FDIA direction")
        z = z + direction * (_tier_sigma(tier) / normalized_peak)

    # Timing is independent of the attack label. A small fraction of samples
    # receive ordinary network jitter in every scenario.
    delta_t = max(1e-4, float(rng.normal(0.004, 0.0005)))
    if rng.rand() < 0.20:
        delta_t = max(1e-4, float(rng.normal(0.006, 0.0015)))

    return z, delta_t, {
        "scenario": scenario,
        "severity_tier": "Tier 0 (Benign)" if scenario == "baseline" else tier,
        "attack_magnitude": round(float(attack_magnitude), 8),
        "snr_estimate": round(float(attack_magnitude), 4),
        "attack_mode": attack_mode,
    }


def generate_physical_dataset(case_name: str, num_calibration: int = 200,
                               num_validation: int = 100,
                               num_test_per_scenario: int = 60,
                               seed: int = 42) -> Dict:
    """Create leak-free calibration/validation/test splits from AC power flow."""
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
        sc = attacks[i % len(attacks)]; tier = SEVERITY_TIERS[i % 4]
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
        "test": {"z": np.asarray(test_z), "iat": np.asarray(test_iat),
                 "labels": np.asarray(test_labels), "metadata": metadata},
    }
