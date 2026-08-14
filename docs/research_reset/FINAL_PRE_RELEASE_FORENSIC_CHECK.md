# Phase 5C — Final Pre-Release Forensic Check Report: XMON-Grid

**Date**: August 13, 2026  
**Environment**: Read-Only Forensic Inspection (`results/independent_validation_run/`, `results/tsg_run_002/`)  
**Status**: Pre-Release Forensic Verification Complete  

---

## 1. Primary Pre-Release Forensic Audit Matrix

| CHECK | EVIDENCE | RESULT | STATUS |
| :--- | :--- | :--- | :--- |
| **FC-01: Multi-Seed Metrics Verification** | Evaluated raw 1,200 predictions for Seed 2026 and 5-seed summary table (`multi_seed_summary.csv`) for seeds 2026--2030. | Mean F1 $= 0.9232 \pm 0.0032$, Mean Recall $= 0.8585 \pm 0.0048$, Mean FPR $= 0.0058 \pm 0.0073$, Mean MCC $= 0.7362 \pm 0.0100$. | **PASS** |
| **FC-02: IEEE Case-Wise Verification** | Recalculated confusion matrices from raw 300 test samples per case for Seed 2026. | IEEE 9 (F1: 0.9238, Rec: 0.8583, FPR: 0.0000); IEEE 14 (F1: 0.9058, Rec: 0.8417, FPR: 0.0667); IEEE 30 (F1: 0.9213, Rec: 0.8542, FPR: 0.0000); IEEE 118 (F1: 0.9310, Rec: 0.8708, FPR: 0.0000). | **PASS** |
| **FC-03: Attack Scenario Breakdown Verification** | Evaluated 240 samples per scenario for Seed 2026 across 5 active scenarios (`baseline`, `branch_outage`, `fdia`, `load_shift`, `stealth_drift`). | `baseline` (Recall: 0.0000, FPR: 0.0167); `branch_outage` (Recall: 0.9833, F1: 0.9916); `fdia` (Recall: 0.9833, F1: 0.9916); `load_shift` (Recall: 0.7542, F1: 0.8599); `stealth_drift` (Recall: 0.7042, F1: 0.8264). | **PASS** |
| **FC-04: Confusion Matrix Exactness** | Raw sample summation across Seed 2026 test predictions ($N=1200$). | $\text{TN} = 236$, $\text{FP} = 4$, $\text{FN} = 138$, $\text{TP} = 822$. $\text{Precision} = 0.9952$, $\text{Recall} = 0.8562$, $\text{F1} = 0.9205$. | **PASS** |
| **FC-05: Effect Size & Statistical Unit Audit** | Evaluated Cohen's $d$ on 1,200-sample binary decision vectors. | $K=2$ vs NIS ($d = -0.2621$); $K=2$ vs CUSUM ($d = -0.2269$); $K=2$ vs Jitter ($d = 2.0746$); $K=2$ vs Sequential ($d = 0.0161$). Statistical unit is sample decision vector. | **PASS** |
| **FC-06: Historical Export Artifact Investigation** | Inspected `tsg_run_002/metrics/detector_outputs.csv` vs `tsg_run_002/tables/comparative_results.csv` vs markdown summary reports. | Raw CSVs in `tsg_run_002` are valid and distinct (NIS F1: 0.8707, CUSUM F1: 0.9969, Jitter F1: 0.0267, K=2 F1: 0.9341). Export artifact affected only early markdown report text, NOT raw CSV data. | **PASS** |
| **FC-07: Independent Package Export Integrity** | Audited `results/independent_validation_run/audit/*.csv` exporter functions. | All 6 audit CSVs generated directly from raw prediction vectors without string formatting or aggregation shortcuts. | **PASS** |
| **FC-08: Calibration / Test Isolation** | Inspected calibration data array shapes and labels. | Calibration set contains 200 benign-only samples (label 0). Estimator and detector states reset prior to test evaluation. Zero test label leakage. | **PASS** |
| **FC-09: Seed Diversity & Non-Determinism** | Calculated element-wise max absolute difference of NIS outputs between Seed 2026 and Seed 2027. | Max NIS difference $= 18.4921$ p.u., confirming true random seed variation across independent runs. | **PASS** |
| **FC-10: Cross-Package Zero Copying** | Compared raw prediction hashes and metric values between `tsg_run_002` and `independent_validation_run`. | `tsg_run_002` F1 $= 0.9341$ (Seed 42) vs `independent_validation_run` F1 $= 0.9205$ (Seed 2026). Zero copied numbers. | **PASS** |
| **FC-11: Figure-to-CSV Fidelity** | Verified rendered PNG file sizes and data coordinates against raw CSV sources. | `fig1_roc_curve.png` (122,911 bytes) and `fig2_pr_curve.png` (106,758 bytes) rendered 100% directly from `s_comp` CSV vectors. | **PASS** |

---

## 2. Reconciliation Matrix: Historical vs Fresh Independent Results

| OLD RESULT (`tsg_run_002`, Seed 42) | NEW RESULT (`independent_validation_run`, Seed 2026) | WHICH IS AUTHORITATIVE | REASON |
| :--- | :--- | :--- | :--- |
| **$K=2$ Quorum F1**: `0.9341` | **$K=2$ Quorum F1**: `0.9205` | Both valid for their respective random seeds; `independent_validation_run` is primary for multi-seed stats. | Seed variation (Seed 42 vs Seed 2026). 5-seed mean is $0.9232 \pm 0.0032$. |
| **$K=2$ Quorum Recall**: `0.8781` | **$K=2$ Quorum Recall**: `0.8562` | Both valid for their respective random seeds. | Seed variation across sample noise realizations. 5-seed mean Recall is $0.8585 \pm 0.0048$. |
| **$K=2$ Quorum FPR**: `0.0083` | **$K=2$ Quorum FPR**: `0.0167` | Both valid for their respective random seeds. | 5-seed mean FPR is $0.0058 \pm 0.0073$. |
| **NIS Standalone F1**: `0.8707` | **NIS Standalone F1**: `0.8585` | `independent_validation_run` (Seed 2026). | Both raw CSVs are valid. Independent run provides complete audit package in `audit/`. |
| **CUSUM Standalone F1**: `0.9969` | **CUSUM Standalone F1**: `0.9858` | `independent_validation_run` (Seed 2026). | Minor variation in benign calibration sample threshold bounds across seeds. |
| **Jitter Standalone F1**: `0.0267` | **Jitter Standalone F1**: `0.0083` | `independent_validation_run` (Seed 2026). | Jitter detector triggers primarily on dynamic timing anomalies, yielding low F1 on static measurements. |
| **Markdown Text Report Artifact**: `0.9341` (Collapsing all rows in historical text summary) | **Audit CSV Table**: Distinct per-method metrics (`audit_method_performance.csv`) | `independent_validation_run/audit/audit_method_performance.csv` | Historical markdown report text collapsed rows during formatting. Raw CSV files in both packages have always been distinct and uncorrupted. |

---

## 3. Final Pre-Release Forensic Verdict

### **RELEASE-READY**

*(All 11 forensic check items have passed 100%. Raw prediction CSVs, seed diversity, confusion matrices, case/attack breakdowns, effect sizes, calibration isolation, and figure-to-CSV fidelity are completely verified and audit-compliant.)*

---

## 4. Final Remaining Administrative Steps Prior to Tagging

1. **User Request for Manuscript Figure Refresh**: Receive explicit user directive to copy fresh figures from `results/independent_validation_run/figures/` into paper graphics directories.
2. **Tag Creation**: Execute `git tag v2.4-paper-final` or `git tag ieee-tx-submission-candidate-v1`.
3. **Repository Commit & Push**: Commit verified validation documents (`docs/research_reset/`) and push to remote.
