# Phase 5P — Professional Repository Cleanup Manifest Report

**Date**: August 14, 2026  
**Environment**: Repository Organizational Maintenance & Archival Planning  
**Target Release**: IEEE Transactions Submission (`v1.2-validated-experimental-release`)  
**Status**: Cleanup Manifest Created  

---

## 1. Master Cleanup & Archival Mapping Matrix

| PATH | CURRENT ROLE | PROPOSED LOCATION | REASON | SCIENTIFIC RISK | REFERENCES TO UPDATE |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`results/README.txt`** | Stale AEGIS-era text file | `archive/historical_results/aegis_results_README.txt` | References broken paths (`results/final_dataset.csv`) and legacy numbers. | **LOW**: Preserved intact in `archive/`. | None |
| **`run_all.sh`** | Legacy shell driver | `archive/legacy_scripts/run_all.sh` | Echoes "AEGIS-GRID-V2" and references obsolete scripts. | **LOW**: Preserved intact in `archive/`. | `README.md` (remove obsolete reproduction instructions) |
| **`verify_paper_results.sh`** | Legacy shell verifier | `archive/legacy_scripts/verify_paper_results.sh` | Echoes "AEGIS-GRID-V2" and references obsolete scripts. | **LOW**: Preserved intact in `archive/`. | `README.md` |
| **`experiments/real_roc_comparison.py`** | Legacy AEGIS ROC experiment | `archive/legacy_experiments/real_roc_comparison.py` | Uses `aegis_scores` variable and legacy dataset paths. | **LOW**: Preserved intact in `archive/`. | None |
| **`experiments/run_experiment.py`** | Legacy AEGIS experiment driver | `archive/legacy_experiments/run_experiment.py` | Imports `aegis_grid_v2` module. | **LOW**: Preserved intact in `archive/`. | None |
| **`experiments/run_full_xmon_experiment.py`** | Legacy prototype runner | `archive/legacy_experiments/run_full_xmon_experiment.py` | Prototype script superseded by `scripts/run_independent_validation.py`. | **LOW**: Preserved intact in `archive/`. | None |

---

## 2. Invariance & Non-Mutation Rules

- **`paper/main.tex`**: **MUST NOT TOUCH** (0 modifications allowed).
- **`core/*.py`**: **MUST NOT TOUCH** (0 modifications allowed).
- **`results/independent_validation_run/`**: **MUST NOT TOUCH** (Authoritative Phase 5 release dataset and paper figures).
- **`results/tsg_run_002/`**: **MUST NOT TOUCH** (Frozen historical reference benchmark).
- **Git Tags**: **MUST NOT TOUCH** (Tag `v1.2-validated-experimental-release` remains anchored to commit `131a92169e0bbed4c5560003f54dce8fdea4712c`).
