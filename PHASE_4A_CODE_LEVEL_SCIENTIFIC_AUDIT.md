# PHASE 4A — PRE-SUBMISSION CODE-LEVEL SCIENTIFIC AUDIT REPORT

**Repository**: XMON-Grid  
**Frozen Experimental Tag**: `v1.0-experimental-freeze`  
**Git Commit**: `17a70f20957f0d0733a92adcf96f51976fd329b4` (matching commit `17a70f...`)  
**Frozen Results Target**: `results/tsg_run_002/`  
**Audit Date**: August 12, 2026  
**Auditor**: Antigravity AI (Advanced Agentic Coding / Scientific Verification Unit)

---

## 1. EXECUTIVE VERDICT

> [!WARNING]
> **VERDICT: NO-GO FOR IMMEDIATE MANUSCRIPT SUBMISSION IN CURRENT FORM (CORRECTIVE EXPERIMENT & REVISION REQUIRED)**

The code-level audit of the frozen XMON-Grid benchmark (`v1.0-experimental-freeze`, `results/tsg_run_002/`) confirms that while the core state estimation mathematics, admittance matrix construction ($Y_{\text{bus}}$), Jacobian formulation ($H$), and baseline Chi-Square NIS calculations are mathematically sound, **there are 2 CRITICAL/HIGH code-level execution flaws and several conceptual discrepancies that invalidate the current comparative claims in the manuscript**:

1. **[CRITICAL] Sequential State Leakage Across Test Scenarios**: In `scripts/run_authoritative_experiment.py`, stateful detectors (`CUSUMDetector` and `SequentialAccumulator`) are reset after calibration, but are **NEVER reset between independent test scenarios** (`baseline` $\rightarrow$ `branch_outage` $\rightarrow$ `fdia` $\rightarrow$ `load_shift` $\rightarrow$ `stealth_drift`). As a result, the first attack scenario (`branch_outage`) drives CUSUM state $g_k$ to $> 10^6$, causing $a_{\text{cusum}} = 1$ to lock permanently ON for 239 out of 240 samples across all subsequent attack scenarios in cases 14, 30, and 118.
2. **[HIGH] Confounded Ablation Study Logic**: In `scripts/run_comparative_ablation_analysis.py`, Ablations B, C, and D ("without NIS", "without CUSUM", "without Jitter") changed the quorum threshold logic from $K=2$ consensus to an **OR gate** (`>= 1`). In Ablation B ("without NIS"), switching to an OR gate allowed CUSUM standalone to pass alarms through directly, raising F1 from 0.9341 to 0.9969 (+0.0628). This artificially framed removing NIS as beneficial, when the F1 gain actually came from dropping the $K=2$ consensus constraint.
3. **[HIGH] Mathematical Identity of XMON $K=2$ and Simple 3-Detector Majority**: XMON-Grid $K=2$ quorum fusion $\mathbb{I}(a_{\text{nis}} + a_{\text{cusum}} + a_{\text{jitter}} \ge 2)$ and Simple 3-Detector Majority Vote $\mathbb{I}(a_{\text{nis}} + a_{\text{cusum}} + a_{\text{jitter}} \ge 2)$ use the exact same binary inputs and decision rule. Direct per-sample comparison on all 1,200 test predictions yields **1,200 identical decisions and 0 discordant decisions ($p = 1.0$)**. Presenting them as distinct competing methods in tables is redundant.
4. **[HIGH] SequentialAccumulator Disconnect**: `SequentialAccumulator` (`a_seq`, $\Theta_k$) is defined in `core/xmon_model.py`, but is **not included in the quorum voting logic** `QuorumLogic.evaluate(a_nis, a_cusum, a_jitter)`. Claims that $K=2$ quorum fusion relies on `SequentialAccumulator` temporal filtering are incorrect; the temporal filtering in $K=2$ comes solely from CUSUM's internal state $g_k$.
5. **[MEDIUM] Lack of Canonical Stealthy FDIA ($a = H c$)**: The benchmark contains no canonical Jacobian-null-space injection attack $a = H c$ designed to bypass WLS residual analysis on unchanged physical states. `fdia` injects raw additive measurement offsets, and `stealth_drift` modifies the physical voltage state vector $x$ directly.

---

## 2. K=2 VS SIMPLE 3-DETECTOR MAJORITY RESULT

### Implementation Analysis
- **XMON-Grid $K=2$ Implementation**: In `core/xmon_model.py` (lines 280–296), `QuorumLogic.evaluate(a_nis, a_cusum, a_jitter)` computes:
  $$\text{votes} = \mathbb{I}(a_{\text{nis}}) + \mathbb{I}(a_{\text{cusum}}) + \mathbb{I}(a_{\text{jitter}}), \quad d_{k2} = \mathbb{I}(\text{votes} \ge 2)$$
- **Simple 3-Detector Majority Implementation**: In `scripts/run_comparative_ablation_analysis.py` (line 108), Method 7 is defined as:
  $$\text{simple\_maj} = \mathbb{I}(a_{\text{nis}} + a_{\text{cusum}} + a_{\text{jitter}} \ge 2)$$

### Direct Decision Vector Comparison (`results/tsg_run_002/metrics/detector_outputs.csv`)
- **Total Test Samples**: 1,200
- **Identical Decisions**: 1,200 (100.00%)
- **Discordant Decisions**: 0 (0.00%)
- **Confusion Matrix Match**: Identical ($\text{TN}=238, \text{FP}=2, \text{FN}=117, \text{TP}=843$)
- **Mathematical Equivalence**: Explicitly proven. Both rules map $\{0,1\}^3 \rightarrow \{0,1\}$ via $f(a_1, a_2, a_3) = \mathbb{I}(a_1 + a_2 + a_3 \ge 2)$.

> [!IMPORTANT]
> **Conclusion**: XMON-Grid $K=2$ and Simple 3-Detector Majority Vote are **mathematically identical**. The confusion matrices being identical is mathematically guaranteed.

---

## 3. ABLATION VALIDITY RESULT

Audit of all six ablations in `scripts/run_comparative_ablation_analysis.py` (lines 185–193):

| Ablation | Code Implementation | Intended Removal | Signal Removed | Signal Remaining | Valid / Causally Interpretable? |
|---|---|---|---|---|---|
| **A. Full XMON-Grid** | `((a_nis + a_cusum + a_jitter) >= 2)` | Baseline | None | NIS, CUSUM, Jitter ($K=2$) | **YES** |
| **B. w/o NIS** | `((a_cusum + a_jitter) >= 1)` | NIS | NIS | CUSUM, Jitter (OR gate) | **NO** (Confounded by OR gate) |
| **C. w/o CUSUM** | `((a_nis + a_jitter) >= 1)` | CUSUM | CUSUM | NIS, Jitter (OR gate) | **NO** (Confounded by OR gate) |
| **D. w/o Jitter** | `((a_nis + a_cusum) >= 1)` | Jitter | Jitter | NIS, CUSUM (OR gate) | **NO** (Confounded by OR gate) |
| **E. w/o Seq Accumulator** | `(s_comp > 0.30)` | SequentialAccumulator | Accumulator | Frame score $S_{\text{comp}} > 0.30$ | **NO** (Accumulator was never in $K=2$) |
| **F. w/o Quorum Fusion** | `(s_comp > 0.50)` | Quorum Logic | Quorum | Frame score $S_{\text{comp}} > 0.50$ | **NO** (Evaluates $S_{\text{comp}}$ threshold, not fusion) |

### Detailed Flaw Breakdown
1. **OR Gate Confounding in B, C, D**: Removing one detector from a 3-detector $K=2$ quorum should yield a 2-detector quorum requiring $K=2$ out of 2 (AND gate: $d_1 \land d_2$). Using an OR gate ($d_1 \lor d_2$) relaxes the consensus requirement from majority to sensitivity mode. In Ablation B, this allowed standalone CUSUM alarms to pass directly, boosting F1 from 0.9341 to 0.9969 (+0.0628) and creating the false impression that NIS degrades performance.
2. **Sequential Accumulator Disconnect in E**: `SequentialAccumulator` ($\Theta_k$) is not part of `QuorumLogic.evaluate`. Thresholding $S_{\text{comp}} > 0.30$ tests an ad-hoc continuous score cutoff, not the removal of sequential accumulation from $K=2$.

---

## 4. SEQUENTIAL ACCUMULATOR AUDIT

Inspect `core/xmon_model.py` and `scripts/run_authoritative_experiment.py`:

1. **Calibration uses BENIGN data only**: **VERIFIED** (`core/data_pipeline.py` L193-200 generates 200 benign samples per case; `calibrate_benign` receives only benign inputs).
2. **Test labels are never used to tune thresholds**: **VERIFIED** (No labels passed during threshold calculation).
3. **Calibration and test samples are disjoint**: **VERIFIED** (PRNG generates calibration, validation, and test splits sequentially with 0 overlap).
4. **Sequential state is reset correctly between independent cases/scenarios**: **FAILED [CRITICAL]** (`model.cusum_detector.reset()` and `model.sequential_accumulator.reset()` are called after calibration at lines 82-84 of `scripts/run_authoritative_experiment.py`, but are **NEVER called between test scenarios** at lines 98-170).
5. **Sequential state cannot leak from one attack/test sequence into another**: **FAILED [CRITICAL]** (Severe state leakage occurred. In `branch_outage`, $g_k$ reached $> 10^6$. Because $g_k$ was not reset when transitioning to `fdia`, `load_shift`, and `stealth_drift`, $g_k$ remained $> 10^6$, locking $a_{\text{cusum}} = 1$ permanently for all subsequent samples).
6. **Threshold is fixed before test evaluation**: **VERIFIED** (Calibrated parameters fixed during test pass).
7. **FPR=0.0000 is genuinely measured on untouched test benign samples**: **VERIFIED** for `SequentialAccumulator` standalone (`a_seq` has 0 FPs on 240 benign test samples). For $K=2$, FPR = $2/240 = 0.0083$.

### Traceability Table
- `core/xmon_model.py`:
  - `CUSUMDetector.update` & `reset`: Lines 155–186
  - `SequentialAccumulator.update`, `calibrate`, & `reset`: Lines 252–275
  - `XMONGridModel.calibrate_benign`: Lines 316–348
- `scripts/run_authoritative_experiment.py`:
  - Calibration execution: Lines 66–79
  - Detector reset after calibration: Lines 81–84
  - Un-reset test loop across 5 scenarios: Lines 98–170

---

## 5. DATA LEAKAGE / SPLIT AUDIT

- **Calibration Set**: 800 benign-only samples (200 per IEEE case) — **CONFIRMED**
- **Validation Set**: 400 samples (100 per IEEE case, 50% benign / 50% attack) — **CONFIRMED**
- **Test Set**: 1,200 samples (300 per IEEE case: 60 benign + 240 attack) — **CONFIRMED**
- **Test Samples in Calibration**: **0 (Verified)**
- **Test Labels in Calibration**: **0 (Verified)**
- **Duplicate Rows Across Splits**: **0 (Verified)**
- **Hidden Label Use in Detectors**: **None (Verified)**
- **Random Seed Provenance**: **Deterministic (`seed=42`)**

---

## 6. TEMPORAL / EVENT-LEVEL VALIDITY

- **Snapshot vs Continuous Event**: The 1,200 test samples are **synthetic i.i.d. snapshot samples** where severity tiers alternate on every sample (`Tier 1` $\rightarrow$ `Tier 2` $\rightarrow$ `Tier 3` $\rightarrow$ `Tier 4` $\rightarrow$ `Tier 1`...). They are **not continuous time-series trajectories** of single attack events.
- **Event-Level Analysis Availability**: If each 60-sample scenario block is treated as 1 attack event (total 16 attack events across 4 cases $\times$ 4 attack types):
  - **Total Attack Events**: 16
  - **Events Detected by $K=2$**: 16 / 16 (100% event detection rate)
  - **Missed Events**: 0
  - **First Detection Cycle**: Cycle 0 for `case9` (all scenarios) and Cycle 1 for `branch_outage` in `case14`, `case30`, `case118`.
  - **State Leakage Artifact**: For scenarios 2, 3, and 4 (`fdia`, `load_shift`, `stealth_drift`), un-reset CUSUM state forced first detection cycle to 0 artificially.

---

## 7. McNEMAR STATISTICAL COMPARISON RESULTS

Evaluated on all 1,200 identical test predictions from `results/tsg_run_002/metrics/detector_outputs.csv`:

| Comparison | Discordant Pairs ($b, c$) | McNemar Stat (cc) | Exact Binomial $p$-value | Statistical Interpretation |
|---|---|---|---|---|
| **XMON $K=2$ vs Simple Majority** | $b=0, c=0$ ($b+c=0$) | 0.0000 | $p = 1.0000$ | **Mathematically Identical** (Exact match) |
| **XMON $K=2$ vs CUSUM Standalone** | $b=1, c=114$ ($b+c=115$) | 109.0783 | $p = 5.59 \times 10^{-33}$ | **CUSUM Standalone is Statistically Superior** ($p < 0.0001$) |
| **XMON $K=2$ vs Sequential-Only** | $b=11, c=116$ ($b+c=127$) | 85.1654 | $p = 2.88 \times 10^{-23}$ | **Sequential-Only is Statistically Superior** ($p < 0.0001$) |

*Note: $b$: XMON $K=2$ correct & Opponent wrong; $c$: XMON $K=2$ wrong & Opponent correct.*

---

## 8. MCC & BALANCED ACCURACY RESULTS

Calculated directly from frozen per-sample predictions (`detector_outputs.csv`):

| Method | Accuracy | Precision | Recall | F1-Score | FPR | Specificity | Balanced Accuracy | MCC |
|---|---|---|---|---|---|---|---|---|
| **CUSUM Standalone** | **0.9950** | 0.9969 | 0.9969 | **0.9969** | 0.0125 | 0.9875 | **0.9922** | **0.9844** |
| **Sequential-Only** | 0.9883 | **1.0000** | 0.9854 | 0.9927 | **0.0000** | **1.0000** | 0.9927 | 0.9649 |
| **Simple Majority** | 0.9008 | 0.9976 | 0.8781 | 0.9341 | 0.0083 | 0.9917 | 0.9349 | 0.7623 |
| **XMON $K=2$ (Strict Majority)** | 0.9008 | 0.9976 | 0.8781 | 0.9341 | 0.0083 | 0.9917 | 0.9349 | 0.7623 |
| **XMON $K=1$ (Sensitivity Mode)** | 0.8892 | 0.8783 | **1.0000** | 0.9352 | 0.5542 | 0.4458 | 0.7229 | 0.6258 |
| **NIS Standalone** | 0.7917 | 0.8645 | 0.8771 | 0.8707 | 0.5500 | 0.4500 | 0.6635 | 0.3346 |
| **Jitter Standalone** | 0.2108 | 1.0000 | 0.0135 | 0.0267 | 0.0000 | 1.0000 | 0.5068 | 0.0523 |

---

## 9. STEALTH-FDIA GAP AUDIT

- **Canonical Stealth FDIA ($a = H c$) Present**: **NO**
- **Current Implementation**:
  - `attack_type == "fdia"`: Direct additive measurement offsets $a = [v_{\text{off}}, pq_{\text{off}}]^T$.
  - `attack_type == "stealth_drift"`: Direct offset added to physical bus voltage states $x_{\text{state}}[N-1:]$, evaluated through AC power flow $h(x)$.
- **Scientific Gap**: A canonical stealthy FDIA satisfies $a = H c$ or $z_{\text{attack}} = h(x) + H c + e$. Because $a \in \text{range}(H)$, the linear innovation residual $r = z - H \hat{x} = 0$, rendering the attack mathematically invisible to NIS residual detectors.
- **Required Implementation for Valid Benchmark Extension**: Construct $a_k = H(x_k) c_k$ for arbitrary state perturbation $c_k$ and inject into measurement $z_{\text{meas}} = h(x_{\text{nominal}}) + a_k + e$.

---

## 10. PHYSICAL / SIMULATION TERMINOLOGY AUDIT

| Claim Term | Justified by Current Experiment? | Status & Recommended Replacement |
|---|---|---|
| `"real-world"` | **NO** | [LOW] Replace with `"simulated IEEE benchmark power systems"`. |
| `"real SCADA"` | **NO** | [LOW] Replace with `"simulated SCADA telemetry and timing model"`. |
| `"field validation"` | **NO** | [LOW] Replace with `"synthetic AC power flow experimental evaluation"`. |
| `"deployment"` | **NO** | [LOW] Replace with `"simulated pipeline evaluation"`. |
| `"physical validation"`| **PARTIALLY** | [LOW] Replace with `"physics-informed AC power flow simulation"`. |
| `"real-time"` | **PARTIALLY** | [LOW] Replace with `"low-latency single-frame processing"`. |

---

## 11. SCALABILITY CLAIM AUDIT

- **Tested Cases**: `case9`, `case14`, `case30`, `case118` (Max dimension $N=118$, $m=354$).
- **Computational Complexity**: Dense state estimation requires matrix inversion/solves of size $m \times m$, yielding $O(N^3)$ time complexity per sample using `np.linalg.solve`.
- **Scalability Finding**: Testing on synthetic IEEE cases up to 118 buses does not demonstrate scalability to multi-thousand bus utility grids without sparse matrix solvers.
- **Recommended Revision Wording**: `"validated across IEEE benchmark systems of increasing dimension from 9 to 118 buses."`

---

## 12. SINGLE-SOURCE-OF-TRUTH METRIC AUDIT

Direct recalculation of all metrics from `results/tsg_run_002/metrics/detector_outputs.csv` confirms:
- **Discrepancy between raw predictions and `main_results.csv`**: **0.000000 (100% Exact Match)**
- **Discrepancy between raw predictions and `comparative_results.csv`**: **0.000000 (100% Exact Match)**
- Stored table metrics are faithfully computed from the stored raw CSV.

---

## 13. EXACT ISSUES REQUIRING FIX

1. **[CRITICAL] Issue 1**: Un-reset CUSUM/Sequential state between test scenario boundaries in `scripts/run_authoritative_experiment.py`.
2. **[HIGH] Issue 2**: Flawed ablation logic in `scripts/run_comparative_ablation_analysis.py` (switching to OR gate in Ablations B, C, D and ad-hoc thresholding in E, F).
3. **[HIGH] Issue 3**: Claiming XMON $K=2$ outperforms Simple 3-Detector Majority when they are mathematically identical.
4. **[HIGH] Issue 4**: Presenting `SequentialAccumulator` as part of $K=2$ quorum fusion when it is not wired into `QuorumLogic.evaluate`.
5. **[MEDIUM] Issue 5**: Absence of canonical $a = H c$ stealthy FDIA in the attack suite.
6. **[LOW] Issue 6**: Overbroad physical deployment and real-world terminology.

---

## 14. EXPERIMENTS THAT MUST BE RERUN

- **Re-running Authoritative Experiment (with detector reset between scenarios)**: MUST BE RERUN to produce clean, un-polluted sequential state traces and accurate standalone CUSUM / $K=2$ performance metrics.
- **Corrected Ablation Study**: MUST BE RERUN using consistent quorum consensus rules (e.g. 2-out-of-2 AND gate $d_1 \land d_2$ or fixed ratio quorum).

---

## 15. EXPERIMENTS THAT DO NOT NEED RERUNNING

- **State Estimator & Grid Topology Code**: Core AC power flow equations, $Y_{\text{bus}}$ construction, and Jacobian calculations in `core/grid_topology.py` and `core/xmon_model.py` are mathematically sound.
- **Data Generation Logic**: Noise generation, nominal states, and severity tier definitions in `core/data_pipeline.py` do not need structural modification (except adding $a=Hc$ if desired).

---

## 16. FINAL GO/NO-GO DECISION

```
================================================================================
FINAL VERDICT: NO-GO (PHASE 4A AUDIT COMPLETE)
================================================================================
The manuscript cannot be submitted in its current state.
Required actions before Phase 4B manuscript revision:
1. Fix `scripts/run_authoritative_experiment.py` to call `.reset()` on all
   stateful detectors between test scenarios.
2. Fix `scripts/run_comparative_ablation_analysis.py` to use mathematically
   sound ablation quorum logic.
3. Rerun the experiment script to generate clean frozen results (e.g. `tsg_run_003`).
4. Update manuscript text to clarify that XMON K=2 IS the 3-detector majority vote
   and adjust comparative framing accordingly.
================================================================================
```

---
*Report generated and frozen as read-only artifact `PHASE_4A_CODE_LEVEL_SCIENTIFIC_AUDIT.md`.*
