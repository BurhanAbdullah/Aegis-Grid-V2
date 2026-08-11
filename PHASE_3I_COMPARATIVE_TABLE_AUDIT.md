# PHASE 3I — FINAL COMPARATIVE TABLE COMPLETENESS AUDIT REPORT

**Date**: 2026-08-11  
**Repository Branch**: `tsg-clean-reproduction`  
**Git Commit Hash**: `395d4cf1ab22f4061f49de23fa9b1e4c48407df2`  
**Target Directory**: `results/tsg_run_002/tables/`  
**Audit Mode**: Read-Only File & Metric Completeness Verification

---

## EXECUTIVE DECISION & VERDICT

### **FINAL VERDICT**: **GO — ALL COMPARATIVE TABLES COMPLETE**

---

## 1. EVALUATED COMPARATIVE METHODS VERIFICATION (`comparative_results.csv`)

The file [`results/tsg_run_002/tables/comparative_results.csv`](file:///C:/Users/burha/.gemini/antigravity/scratch/XMON-Grid/results/tsg_run_002/tables/comparative_results.csv) contains **EXACTLY 10 methods**, evaluated on 1,200 identical test samples:

| # | Stored Method Name | TN | FP | FN | TP | Accuracy | Precision | Recall | F1-Score | FPR | ROC-AUC | PR-AUC |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `1. NIS Standalone` | 108 | 132 | 118 | 842 | 0.7917 | 0.8645 | 0.8771 | 0.8707 | 0.5500 | 0.8379 | 0.9388 |
| 2 | `2. CUSUM Standalone` | 237 | 3 | 3 | 957 | 0.9950 | 0.9969 | 0.9969 | 0.9969 | 0.0125 | 0.9993 | 0.9998 |
| 3 | `3. Jitter Standalone` | 240 | 0 | 947 | 13 | 0.2108 | 1.0000 | 0.0135 | 0.0267 | 0.0000 | 0.6262 | 0.8509 |
| 4 | `4. NIS + CUSUM (OR)` | 107 | 133 | 0 | 960 | 0.8892 | 0.8783 | 1.0000 | 0.9352 | 0.5542 | N/A | N/A |
| 5 | `5. NIS + Jitter (OR)` | 108 | 132 | 114 | 846 | 0.7950 | 0.8650 | 0.8812 | 0.8731 | 0.5500 | N/A | N/A |
| 6 | `6. CUSUM + Jitter (OR)` | 237 | 3 | 3 | 957 | 0.9950 | 0.9969 | 0.9969 | 0.9969 | 0.0125 | N/A | N/A |
| 7 | `7. Simple 3-Detector Majority Vote` | 238 | 2 | 117 | 843 | 0.9008 | 0.9976 | 0.8781 | 0.9341 | 0.0083 | N/A | N/A |
| 8 | `8. Sequential-Only Detector` | 240 | 0 | 14 | 946 | 0.9883 | 1.0000 | 0.9854 | 0.9927 | 0.0000 | 0.9987 | 0.9997 |
| 9 | `9. XMON-Grid K=2 (Strict Majority)` | 238 | 2 | 117 | 843 | 0.9008 | 0.9976 | 0.8781 | 0.9341 | 0.0083 | 0.9924 | 0.9981 |
| 10 | `10. XMON-Grid K=1 (Sensitivity Mode)` | 107 | 133 | 0 | 960 | 0.8892 | 0.8783 | 1.0000 | 0.9352 | 0.5542 | 0.9924 | 0.9981 |

* **Verification**: Sum of $\text{TN} + \text{FP} + \text{FN} + \text{TP} = 1,200$ across all 10 rows. Zero discrepancy vs `detector_outputs.csv`.

---

## 2. CASE-WISE COMPARISON AUDIT (`case_wise_comparison.csv`)

* **Row Count**: 20 data rows (5 core methods $\times$ 4 IEEE Cases: `case9`, `case14`, `case30`, `case118`).
* **Represented Methods**:
  1. `XMON-Grid K=2`
  2. `XMON-Grid K=1`
  3. `NIS Standalone`
  4. `CUSUM Standalone`
  5. `Jitter Standalone`
* **Sample Sum Verification**:
  * `case9`: 300 test samples per method
  * `case14`: 300 test samples per method
  * `case30`: 300 test samples per method
  * `case118`: 300 test samples per method
  * **Total per method**: $300 \times 4 = \mathbf{1,200 \text{ test samples}}$.

---

## 3. ATTACK-WISE COMPARISON AUDIT (`attack_wise_comparison.csv`)

* **Row Count**: 25 data rows (5 core methods $\times$ 5 scenarios: `baseline`, `branch_outage`, `fdia`, `load_shift`, `stealth_drift`).
* **Represented Methods**:
  1. `XMON-Grid K=2`
  2. `XMON-Grid K=1`
  3. `NIS Standalone`
  4. `CUSUM Standalone`
  5. `Jitter Standalone`
* **Sample Sum Verification**:
  * `baseline` (Benign): 240 samples per method
  * `branch_outage`: 240 samples per method
  * `fdia`: 240 samples per method
  * `load_shift`: 240 samples per method
  * `stealth_drift`: 240 samples per method
  * **Total per method**: $240 \times 5 = \mathbf{1,200 \text{ test samples}}$.

---

## 4. ABLATION STUDY AUDIT (`ablation_results.csv`)

The file [`results/tsg_run_002/tables/ablation_results.csv`](file:///C:/Users/burha/.gemini/antigravity/scratch/XMON-Grid/results/tsg_run_002/tables/ablation_results.csv) contains **EXACTLY 6 configurations**:

| # | Configuration Name | TN | FP | FN | TP | Precision | Recall | F1-Score | FPR | ROC-AUC | PR-AUC |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `A. Full XMON-Grid (K=2 Quorum)` | 238 | 2 | 117 | 843 | 0.9976 | 0.8781 | 0.9341 | 0.0083 | 0.9924 | 0.9981 |
| 2 | `B. XMON-Grid without NIS` | 237 | 3 | 3 | 957 | 0.9969 | 0.9969 | 0.9969 | 0.0125 | N/A | N/A |
| 3 | `C. XMON-Grid without CUSUM` | 108 | 132 | 114 | 846 | 0.8650 | 0.8812 | 0.8731 | 0.5500 | N/A | N/A |
| 4 | `D. XMON-Grid without Jitter` | 107 | 133 | 0 | 960 | 0.8783 | 1.0000 | 0.9352 | 0.5542 | N/A | N/A |
| 5 | `E. XMON-Grid without Sequential Accumulator` | 98 | 142 | 0 | 960 | 0.8711 | 1.0000 | 0.9311 | 0.5917 | 0.8379 | 0.9388 |
| 6 | `F. XMON-Grid without Quorum Fusion` | 235 | 5 | 92 | 868 | 0.9943 | 0.9042 | 0.9471 | 0.0208 | 0.9924 | 0.9981 |

* **Verification**: Recalculations directly from `detector_outputs.csv` match all 6 ablation rows with zero discrepancy.

---

## 5. SEVERITY BREAKDOWN AUDIT (`severity_comparison.csv`)

The file [`results/tsg_run_002/tables/severity_comparison.csv`](file:///C:/Users/burha/.gemini/antigravity/scratch/XMON-Grid/results/tsg_run_002/tables/severity_comparison.csv) contains **20 data rows** (5 core methods $\times$ 5 severity tiers):

| Severity Tier | Sample Count per Method | Total Samples Across 5 Tiers |
|---|---|---|
| `Tier 0 (Benign)` | 240 samples | 240 |
| `Tier 1 (Subtle)` | 240 samples | 240 |
| `Tier 2 (Moderate)` | 240 samples | 240 |
| `Tier 3 (Strong)` | 240 samples | 240 |
| `Tier 4 (Severe)` | 240 samples | 240 |
| **TOTAL** | **1,200 samples per method** | **1,200** |

* **Verification**: Exact match ($240 \times 5 = 1,200$).

---

## 6. AUC / PR-AUC MATHEMATICAL VALIDITY CHECK
* **Continuous Methods**: `NIS Standalone`, `CUSUM Standalone`, `Jitter Standalone`, `Sequential-Only`, `XMON-Grid K=2`, `XMON-Grid K=1` evaluate ROC-AUC and PR-AUC on continuous underlying scores (`nis`, `cusum_g`, `jitter_bar`, `theta_seq`, `s_comp`).
* **Binary-Only Combinations**: `NIS + CUSUM (OR)`, `NIS + Jitter (OR)`, `CUSUM + Jitter (OR)`, `3-Detector Majority Vote` report `N/A` for ROC-AUC and PR-AUC, preserving mathematical rigor without fabricating scores.

---

## 7. FINAL VERDICT

```text
=====================================================================
                    FINAL SCIENTIFIC VERDICT                         
=====================================================================
  [DECISION]            : GO — ALL COMPARATIVE TABLES COMPLETE
  [GROUND TRUTH SAMPLES]: 1,200 (240 Benign + 960 Physical Attack)
  [COMPARATIVE METHODS ]: 10 / 10 Evaluation Methods Present & Verified
  [ABLATION CONFIGS]    : 6 / 6 Ablation Configurations Present & Verified
  [RE-RUN REQUIRED]     : NO (100% Completeness & Internal Consistency)
=====================================================================
```
