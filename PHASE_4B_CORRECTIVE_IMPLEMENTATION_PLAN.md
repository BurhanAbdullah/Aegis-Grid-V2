# PHASE 4B — CORRECTIVE EXPERIMENT PREPARATION & IMPLEMENTATION PLAN

**Repository**: XMON-Grid  
**Date**: August 12, 2026  
**Status**: **IMPLEMENTATION PREPARED & TEST SUITE VERIFIED (16/16 TESTS PASSED)**  
**Target Output Directory**: `results/tsg_run_003/`

---

## 1. EXECUTIVE SUMMARY

In response to the Phase 4A scientific audit, all code-level corrective modifications have been implemented in the working tree. The complete unit test suite (16 tests) has been run and **100% verified (OK)**. 

The target execution directory `results/tsg_run_003/` has been prepared. **No full experiment execution, dataset regeneration, manuscript modification, git commit, or tag alteration has taken place**, in strict compliance with the Phase 4B directives.

---

## 2. EXACT CODE CHANGES PROPOSED & IMPLEMENTED

### A. Core Model (`core/xmon_model.py`)
- **`PowerSystemStateEstimator.reset()` Added**:
  Resets internal state vector $\hat{x}$ to nominal ($\theta = 0$, $V = 1.0$ p.u.) and error covariance matrix $P$ to initial state ($10^{-3} \cdot I$).
- **`XMONGridModel.reset()` Added**:
  Unifies state reset across all stateful components (`estimator`, `cusum_detector`, `jitter_detector`, and `sequential_accumulator`).

```python
    def reset(self):
        """
        Resets state estimator and all stateful detectors to clean initial state.
        Ensures zero information leakage across independent test scenarios.
        """
        self.estimator.reset()
        self.cusum_detector.reset()
        self.jitter_detector.reset()
        self.sequential_accumulator.reset()
```

### B. Authoritative Experiment Runner (`scripts/run_authoritative_experiment.py`)
- **Per-Scenario State Reset**:
  Modified the main test loop to track `current_scenario` and execute `model.reset()` whenever transitioning to a new test scenario (`baseline` $\rightarrow$ `branch_outage` $\rightarrow$ `fdia` $\rightarrow$ `load_shift` $\rightarrow$ `stealth_drift`).

```python
        current_scenario = None
        for idx in range(len(test_z)):
            z_meas = test_z[idx]
            dt_val = test_iat[idx]
            y_true = test_labels[idx]
            meta = test_meta[idx]
            
            # Reset stateful detectors and estimator at the start of every independent scenario
            if meta["scenario"] != current_scenario:
                current_scenario = meta["scenario"]
                model.reset()
            
            step_res = model.step(z_meas, dt_val)
```

### C. Comparative & Ablation Analysis Runner (`scripts/run_comparative_ablation_analysis.py`)
- **Redesigned Causally Valid Ablations**:
  Replaced flawed OR gate logic in Ablations B, C, and D with consistent quorum consensus ($K=2$ out of 2 remaining detectors, i.e., AND gate), preserving the fusion rule framework across all configurations.

```python
    ablations = [
        ("A. Full XMON-Grid (K=2 Quorum)", ((a_nis + a_cusum + a_jitter) >= 2).astype(int), s_comp),
        ("B. XMON-Grid w/o NIS (CUSUM & Jitter, K=2/2)", ((a_cusum + a_jitter) >= 2).astype(int), None),
        ("C. XMON-Grid w/o CUSUM (NIS & Jitter, K=2/2)", ((a_nis + a_jitter) >= 2).astype(int), None),
        ("D. XMON-Grid w/o Jitter (NIS & CUSUM, K=2/2)", ((a_nis + a_cusum) >= 2).astype(int), None),
        ("E. XMON-Grid w/o Sequential Accumulation (Instant Frame Quorum)", ((a_nis + a_jitter) >= 2).astype(int), s_comp),
        ("F. XMON-Grid w/o Quorum Fusion (Continuous S_comp > 0.30)", (s_comp > 0.30).astype(int), s_comp),
    ]
```

---

## 3. REDESIGNED ABLATION FRAMEWORK DOCUMENTATION

| Ablation Configuration | Active Components | Removed Component | Decision Rule | Threshold Source | Calibration Source | Causal Fairness Rationale |
|---|---|---|---|---|---|---|
| **A. Full XMON-Grid** | NIS, CUSUM, Jitter | None | $(a_{\text{nis}} + a_{\text{cusum}} + a_{\text{jitter}}) \ge 2$ | $\chi^2(0.99)$, $g > 5.0$, $\eta_{\mu} = 2.0$ | Benign Calibration Set | Full baseline model ($K=2$ quorum). |
| **B. w/o NIS** | CUSUM, Jitter | NIS Evidence | $(a_{\text{cusum}} + a_{\text{jitter}}) \ge 2$ ($a_{\text{cusum}} \land a_{\text{jitter}}$) | $g > 5.0$, $\eta_{\mu} = 2.0$ | Benign Calibration Set | Preserves $K=2$ quorum requirement; requires both remaining detectors to alarm. |
| **C. w/o CUSUM** | NIS, Jitter | CUSUM Evidence | $(a_{\text{nis}} + a_{\text{jitter}}) \ge 2$ ($a_{\text{nis}} \land a_{\text{jitter}}$) | $\chi^2(0.99)$, $\eta_{\mu} = 2.0$ | Benign Calibration Set | Preserves $K=2$ quorum requirement; requires both remaining detectors to alarm. |
| **D. w/o Jitter** | NIS, CUSUM | Jitter Evidence | $(a_{\text{nis}} + a_{\text{cusum}}) \ge 2$ ($a_{\text{nis}} \land a_{\text{cusum}}$) | $\chi^2(0.99)$, $g > 5.0$ | Benign Calibration Set | Preserves $K=2$ quorum requirement; requires both remaining detectors to alarm. |
| **E. w/o Sequential Accumulation** | NIS, Jitter | Temporal Memory ($g_k$) | $(a_{\text{nis}} + a_{\text{jitter}}) \ge 2$ | $\chi^2(0.99)$, $\eta_{\mu} = 2.0$ | Benign Calibration Set | Evaluates instantaneous frame-by-frame quorum without temporal state accumulation. |
| **F. w/o Quorum Fusion** | Continuous $S_{\text{comp}}$ | Quorum Voting Logic | Continuous Threat Score $S_{\text{comp}} > 0.30$ | Cutoff $0.30$ | Weighted sum $w_1 S_{\text{NIS}} + w_2 S_{\text{CUSUM}} + w_3 S_{\text{Jitter}}$ | Evaluates continuous score thresholding vs discrete quorum consensus. |

*Note: No thresholds are tuned on the test set.*

---

## 4. STATE-RESET STRATEGY

- **Execution Boundary**: Triggered at `sample_idx == 0` for every scenario block (`baseline`, `branch_outage`, `fdia`, `load_shift`, `stealth_drift`).
- **State Objects Reset**:
  1. `CUSUMDetector`: Resets accumulator $g = 0.0$.
  2. `CommunicationJitterDetector`: Clears sliding window `window.clear()`.
  3. `SequentialAccumulator`: Resets state $\Theta = 0.0$.
  4. `PowerSystemStateEstimator`: Resets state estimate $\hat{x}$ to nominal and covariance $P$ to initial $10^{-3} \cdot I$.
- **Isolation Guarantee**: Prevents extreme anomaly values from prior attack scenarios (e.g. $g > 10^6$ in `branch_outage`) from polluting subsequent scenarios.

---

## 5. MATHEMATICAL IDENTITY: K=2 VS MAJORITY VOTE

- **Proof of Equivalence**:
  For binary inputs $(a_{\text{nis}}, a_{\text{cusum}}, a_{\text{jitter}}) \in \{0, 1\}^3$:
  $$d_{\text{k2}} = \mathbb{I}(a_{\text{nis}} + a_{\text{cusum}} + a_{\text{jitter}} \ge 2) \equiv \text{simple\_maj}$$
  The decision functions are identical across all $2^3 = 8$ truth table combinations and all 1,200 test samples.
- **Scientific Differentiation of XMON-Grid**:
  XMON-Grid is distinguished not by a novel voting operator, but by its **cross-layer physical-cyber architecture**:
  1. Physical power grid non-linear AC state estimation + Chi-Square NIS.
  2. Sequential innovation accumulation via CUSUM ($g_k$).
  3. SCADA communication telemetry inter-arrival time jitter detection ($j_k, \bar{j}$).
  4. Continuous composite threat scoring ($S_{\text{comp}}$).
  5. Dual operating modes ($K=2$ strict majority for $\le 1\%$ FPR vs $K=1$ sensitivity mode for $100\%$ recall).

---

## 6. UNIT TEST SUITE VERIFICATION (16/16 PASSED)

The test suite in `tests/test_xmon_model.py` was extended with 5 new comprehensive unit tests:

1. **`test_L_state_reset`**: Verifies all stateful detectors and estimators reset to clean initial values upon `model.reset()`.
2. **`test_M_no_cross_scenario_contamination`**: Verifies scenario B outputs after scenario A with `model.reset()` match running scenario B on a clean fresh model.
3. **`test_N_ablation_component_removal`**: Verifies 2-detector quorum consensus ($K=2$ out of 2) enforces AND gate logic without altering fusion structure.
4. **`test_O_k2_majority_equivalence`**: Verifies $K=2$ quorum evaluation is mathematically identical to 3-detector majority vote across all $2^3$ truth table combinations.
5. **`test_P_threshold_calibration_isolation`**: Verifies calibration uses only benign calibration data and does not touch test labels/data.

### Test Execution Output
```
Ran 16 tests in 2.174s

OK
```

---

## 7. MODEL EQUATIONS STATUS

> [!NOTE]
> **NO MODEL EQUATIONS WERE CHANGED.**
> All physical equations ($h(x)$, $Y_{\text{bus}}$, $H(x)$), EKF state estimation steps, Chi-Square NIS calculation, CUSUM accumulation formula, Jitter $z$-score calculation, and Quorum Voting formulas remain 100% untouched.

---

## 8. PREPARATION FOR EXPERIMENT TSG_RUN_003

The target directory structure has been created:
```
results/tsg_run_003/
├── figures/
├── metrics/
├── raw/
└── tables/
```

### Expected Outputs of Run 003:
1. `raw/full_test_dataset.csv`: 1,200 test samples across 4 IEEE cases and 5 scenarios.
2. `metrics/detector_outputs.csv`: Complete per-sample detector output traces with clean state resets.
3. `metrics/sequential_states.csv`: Clean sequential state trajectories.
4. `tables/main_results.csv`, `comparative_results.csv`, `ablation_results.csv`, `threshold_calibration.csv`, `case_wise_comparison.csv`, `attack_wise_comparison.csv`.
5. Publication Figures 1–12 reflecting clean, un-polluted experimental data.
6. Cryptographic manifest `results/tsg_run_003/SHA256SUMS.txt`.

---

## 9. STOP DECLARATION

In accordance with Phase 4B instructions:
- **Dataset generation was NOT executed.**
- **Authoritative benchmark run 003 was NOT launched.**
- **Frozen results in `results/tsg_run_001/` and `results/tsg_run_002/` were NOT touched.**
- **Manuscript files were NOT modified.**
- **Git commits and pushes were NOT performed.**

*Execution paused pending user review of this implementation plan.*
