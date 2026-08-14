# Figure Manifest: XMON-Grid Publication Figures

This manifest inventories the 11 figures retained in the publication figure set. Unsupported computational-scaling material is deliberately excluded from this release.

| Figure | Description | Source | Evaluation basis | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Fig. 1** | Overall detection-performance comparison | `metrics/detector_outputs.csv` | Primary seed 2026 | VERIFIED |
| **Fig. 2** | $K=1$ vs $K=2$ operating-point trade-off | `metrics/detector_outputs.csv` | Primary seed 2026; not a five-seed comparison | VERIFIED |
| **Fig. 3** | ROC curve | `metrics/detector_outputs.csv` | Primary seed 2026 | VERIFIED |
| **Fig. 4** | Precision--Recall curve | `metrics/detector_outputs.csv` | Primary seed 2026 | VERIFIED |
| **Fig. 5** | Case-wise mean F1 performance | `audit/audit_5seed_case_wise.csv` | Five seeds, 2026--2030 | VERIFIED |
| **Fig. 6** | Attack-wise mean F1 and recall | `audit/audit_5seed_attack_wise.csv` | Five seeds, 2026--2030 | VERIFIED |
| **Fig. 7** | Component ablation study | `audit/audit_ablation_results.csv` | Primary seed 2026 | VERIFIED |
| **Fig. 8** | False-positive/sensitivity trade-off | `comprehensive_comparison.csv` | Primary seed 2026 | VERIFIED |
| **Fig. 9** | Measurement-noise robustness sweep | `robustness_results.csv` | Regenerated robustness experiment | VERIFIED |
| **Fig. 10** | Attack-severity robustness sweep | `robustness_results.csv` | Regenerated robustness experiment | VERIFIED |
| **Fig. 12** | AC power-flow and measurement-equation consistency | `current_physical_sanity.csv` | IEEE 9/14/30/118, independent physical audit | VERIFIED |

## Important provenance notes

- The earlier Fig. 2 claim of $K=2$ recall $=85.85\%$ and FPR $=0.58\%$ was stale and is no longer used.
- The current five-seed $K=2$ aggregate is F1 $=0.9204\pm0.0026$, recall $=0.8850\pm0.0012$, FPR $=0.1525\pm0.0197$, and MCC $=0.6667\pm0.0151$.
- Fig. 12 is generated from the corrected physical audit. The current maximum absolute error across the four cases is below $3\times10^{-14}$ for the audited quantities; no earlier residual value is reused.
- The former computational-scaling figure was removed from the publication set because the current corrected validation run does not independently support its timing claims.
