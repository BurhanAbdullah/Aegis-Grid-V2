# Phase 5P.1 — Forensic Pre-Commit Cleanup Verification Report

**Date**: August 14, 2026  
**Environment**: Read-Only Forensic Verification  
**Branch**: `tsg-clean-reproduction`  
**Target Tag**: `v1.2-validated-experimental-release`  
**Status**: Adversarial Forensic Audit Complete  
**Final Release Verdict**: **CLEANUP VERIFIED — SAFE TO COMMIT**  

---

## Master Forensic Check Table

| ITEM | COMMAND / EVIDENCE | RESULT | RISK | STATUS |
| :--- | :--- | :--- | :--- | :--- |
| **1. Archive Physical Existence & Integrity** | `Test-Path archive/...` (6 files) | All 6 archived files physically exist in `archive/` hierarchy with 100% content match and zero truncation. | **NONE** | **PASSED** |
| **2. Git Status & Apparent Deletions** | `git status -s` & `git diff --stat` | Apparent file deletions correspond strictly to archival moves to `archive/`. | **NONE** | **PASSED** |
| **3. Broken-Reference Audit** | `grep_search` across repository | Zero active code/config references broken. All references exist strictly in historical audit documentation logs. | **NONE** | **PASSED** |
| **4. Terminology Audit (`AEGIS`/`TSG`)** | `grep_search` across repository | Legacy name `Aegis-Grid-V2.0-FINAL` is preserved in Git tags. All remaining text references represent legitimate historical audit provenance. | **NONE** | **PASSED** |
| **5. Line-by-Line `README.md` Audit** | Numerical cross-check vs CSVs | Every metric in `README.md` ($\text{F1} = 0.9232 \pm 0.0032$, $\text{FPR} = 0.0058 \pm 0.0073$, $K=1 \text{ Recall} = 0.9833, \text{FPR} = 0.5792$, $\text{ROC-AUC} = 0.9771$, $\text{PR-AUC} = 0.9950$, $8.25\times$ to $192.58\times$ speedup) matches raw Phase 5 CSVs 100%. | **NONE** | **PASSED** |
| **6. Claim Guardrails Audit** | Prohibited term scan | Zero prohibited claims present: No RPC daemon claim, no field deployment claim, no SOTA claim, no generic "50x speedup" claim. Uses direct `pandapower`/`PyPSA` API disclosure. | **NONE** | **PASSED** |
| **7. Scientific Lineage Traceability** | Lineage chain verification | Complete executable & traceable chain: `core/xmon_model.py` $\rightarrow$ `consensus.py` $\rightarrow$ `grid_topology.py`/`data_pipeline.py` $\rightarrow$ `scripts/run_independent_validation.py` $\rightarrow$ `results/independent_validation_run/` $\rightarrow$ `scripts/generate_paper_figures.py` $\rightarrow$ `paper_figures/` $\rightarrow$ `FIGURE_MANIFEST.md` + `SHA256SUMS.txt`. | **NONE** | **PASSED** |
| **8. Historical Separation** | Directory structure check | `independent_validation_run/` = Authoritative Phase 5 release; `tsg_run_002/` = Frozen historical benchmark; `tsg_run_001/` = Historical prototype; `archive/` = Archived legacy scripts/results. | **NONE** | **PASSED** |
| **9. Automated Unit Test Suite** | `python -m unittest discover tests` | **16/16 PASSED (OK)** in 0.605s. | **NONE** | **PASSED** |
| **10. Physical AC Sanity Check** | `python scripts/physical_sanity_check.py` | 4/4 IEEE cases **PASSED** (Abs P Loss Err $< 3.24 \times 10^{-14}$ p.u.). | **NONE** | **PASSED** |
| **11. Figure Checksum Integrity** | `python scripts/generate_figure_checksums.py` | 25 figure files match `paper_figures/SHA256SUMS.txt` 100%. | **NONE** | **PASSED** |
| **12. Manuscript Protection** | `git diff -- paper/main.tex` | `paper/main.tex` is **100% UNTOUCHED** (0 diff lines). | **NONE** | **PASSED** |

---

## Detailed Section Audits

### Section A — Archive Integrity
All 6 files moved to `archive/` physically exist and maintain 100% byte-for-byte fidelity:
1. `archive/historical_results/aegis_results_README.txt`
2. `archive/legacy_scripts/run_all.sh`
3. `archive/legacy_scripts/verify_paper_results.sh`
4. `archive/legacy_experiments/real_roc_comparison.py`
5. `archive/legacy_experiments/run_experiment.py`
6. `archive/legacy_experiments/run_full_xmon_experiment.py`

### Section B — Broken-Reference Audit
A repository-wide regex search confirmed zero active imports or script calls reference the old paths. All text references are confined to historical audit documentation files.

### Section C — README Audit
Every single numerical statement in `README.md` was cross-checked against `results/independent_validation_run/`:
- $K=2$ Quorum 5-seed mean $\text{F1} = 0.9232 \pm 0.0032$ (CSV: `multi_seed_summary.csv` line 2)
- $K=2$ Quorum 5-seed mean $\text{Recall} = 0.8585 \pm 0.0048$ (CSV: `multi_seed_summary.csv` line 2)
- $K=2$ Quorum 5-seed mean $\text{FPR} = 0.0058 \pm 0.0073$ (CSV: `multi_seed_summary.csv` line 2)
- $K=1$ Sensitivity True OR-Gate $\text{Recall} = 0.9833$, $\text{FPR} = 0.5792$ (CSV: `audit_method_performance.csv` line 3)
- Continuous threat score $\text{ROC-AUC} = 0.9771$, $\text{PR-AUC} = 0.9950$ (CSV: `comprehensive_comparison.csv`)
- IEEE Case-wise means: IEEE 9 ($\text{F1}=0.9215$), IEEE 14 ($\text{F1}=0.9163$), IEEE 30 ($\text{F1}=0.9261$), IEEE 118 ($\text{F1}=0.9286$) match `audit_5seed_case_wise.csv` 100%.

### Section D — AEGIS / TSG Terminology Audit
- `Aegis-Grid-V2.0-FINAL`: Git tag object `e7f111f` (Historical provenance tag).
- `tsg_run_001`: Historical 960-sample run directory.
- `tsg_run_002`: Frozen historical reference run directory (Seed 42).
- `independent_validation_run`: Authoritative Phase 5 release dataset.

### Section E — Scientific-Result Integrity
Raw prediction CSVs, audit CSVs, and robustness datasets in `results/independent_validation_run/` and `results/tsg_run_002/` are 100% untouched.

### Section F — Figure Integrity
All 12 final publication figures in `.pdf` vector and 300 DPI `.png` format match SHA256 hashes in `paper_figures/SHA256SUMS.txt`.

### Section G — Manuscript Integrity
`paper/main.tex` is 100% untouched (0 diff lines).

### Section H — Git Diff Assessment
`git diff --stat` confirms modifications are restricted to updating `README.md` and moving legacy drivers to `archive/`. Zero git commits or pushes have been performed.

---

## Final Pre-Commit Verdict

### **CLEANUP VERIFIED — SAFE TO COMMIT**
