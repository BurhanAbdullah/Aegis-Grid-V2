# Phase 5G — Final Publication Figure Audit Report (Corrected & Renamed)

**Date**: August 14, 2026  
**Environment**: Read-Only Source-of-Truth Verification (`results/independent_validation_run/`)  
**Scope**: 12 Publication Figures, Scientific Presentation Alignment, 5-Seed Aggregates, Renamed Fig 12  
**Status**: Figure Audit Complete  

---

## 1. Figure Audit & Traceability Matrix

| FIGURE | SOURCE CSV FILE | DATA MATCH | VISUAL CHECK | STATUS |
| :--- | :--- | :--- | :--- | :--- |
| **Fig. 1: Overall Performance Comparison** | `metrics/detector_outputs.csv` | **VERIFIED MATCH** (K=2 F1=0.9205, FPR=0.0167; K=1 Rec=0.9833, FPR=0.5792) | Clean IEEE bars, correct legend & labels, zero clipping | **PASSED** |
| **Fig. 2: K=1 vs K=2 Trade-off (5-Seed Aggregate)** | `tables/multi_seed_summary.csv` & `metrics/detector_outputs.csv` | **VERIFIED MATCH** (K=1 OR-Gate Rec=0.9833, FPR=0.5792 vs K=2 5-Seed Rec=$0.8585\pm 0.0048$, FPR=$0.0058\pm 0.0073$) | Clear 5-seed aggregate error bars, 2D crosshair formatting crisp | **PASSED** |
| **Fig. 3: ROC Curve** | `metrics/detector_outputs.csv` | **VERIFIED MATCH** ($\text{ROC-AUC} = 0.9771$) | Smooth monotonic ROC curve, diagonal random baseline | **PASSED** |
| **Fig. 4: Precision–Recall Curve** | `metrics/detector_outputs.csv` | **VERIFIED MATCH** ($\text{PR-AUC} = 0.9950$) | High precision plateau across recall spectrum | **PASSED** |
| **Fig. 5: Case-wise Performance** | `audit/audit_5seed_case_wise.csv` | **VERIFIED MATCH** (IEEE 9: 0.9215, 14: 0.9163, 30: 0.9261, 118: 0.9286) | Bar plot with 5-seed SD error caps, readable text | **PASSED** |
| **Fig. 6: Attack-wise Performance** | `audit/audit_5seed_attack_wise.csv` | **VERIFIED MATCH** (Branch: 0.9933, FDIA: 0.9916, Load: 0.8636, Drift: 0.8263) | Grouped F1 & Recall bars with SD error bars | **PASSED** |
| **Fig. 7: Component Ablation Study** | `audit/audit_ablation_results.csv` | **VERIFIED MATCH** (Ablations A–F F1 and FPR values) | Grouped bars showing NIS & CUSUM contribution | **PASSED** |
| **Fig. 8: False-Positive Trade-off** | `comprehensive_comparison.csv` | **VERIFIED MATCH** (Log-scale FPR vs Recall across methods) | Log-scale x-axis, clear separation of K=2 low FPR | **PASSED** |
| **Fig. 9: Noise Robustness Sweep** | `robustness_results.csv` | **VERIFIED MATCH** (`Exp5_Measurement_Noise_Sweep` $\sigma_v \in [0.0005 .. 0.010]$) | Dual y-axis plot (F1 blue left, FPR red right) | **PASSED** |
| **Fig. 10: Severity Robustness Sweep** | `robustness_results.csv` | **VERIFIED MATCH** (`Exp4_Severity_Sweep` Tiers 1–4 Recall & F1) | Monotonic detection scaling with severity tier | **PASSED** |
| **Fig. 11: Computational Scaling** | `robustness_results.csv` | **VERIFIED MATCH** (`Exp9_Scalability_Latency` IEEE 9--118, $O(N^{0.86})$ fit) | Scatter & $O(N^{0.86})$ log-log fit line, exact speedup callouts | **PASSED** |
| **Fig. 12: AC Power-Flow Numerical Consistency** | `scripts/physical_sanity_check.py` | **VERIFIED MATCH** (Active power loss conservation error bounded below $3.24 \times 10^{-14}$ p.u.) | Log-scale bar chart showing AC power-flow loss error | **PASSED** |

---

## 2. Final Figure Audit Verdict

### **FIGURES READY FOR MANUSCRIPT**
