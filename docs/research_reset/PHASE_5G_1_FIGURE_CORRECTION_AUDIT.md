# Phase 5G.1 — Figure Scientific Correction Audit Report

**Date**: August 14, 2026  
**Environment**: Read-Only Figure Verification (`results/independent_validation_run/paper_figures/`)  
**Scope**: Fig 2 5-Seed Aggregate Error Bars, Fig 12 Title & Scope Correction, Checksum Verification  
**Status**: Scientific Corrections Applied & Verified  

---

## 1. Figure Scientific Correction Matrix

| FIGURE | OLD PRESENTATION | CORRECTED PRESENTATION | SOURCE | VERIFIED |
| :--- | :--- | :--- | :--- | :--- |
| **Fig. 2: K=1 vs K=2 Operating-Point Trade-off** | Plotted Seed 2026 point ($K=2 \text{ FPR}=1.67\%$). | **Updated to 5-Seed Aggregate**: $K=2$ Quorum point plotted with 2D error bars ($\text{Recall} = 0.8585 \pm 0.0048, \text{FPR} = 0.0058 \pm 0.0073$). $K=1$ OR-gate mode clearly labeled ($\text{Recall} = 0.9833, \text{FPR} = 0.5792$). Title updated to: *"Fig. 2 — K=1 vs K=2 Operating-Point Trade-off (5-Seed Aggregates)"*. | `tables/multi_seed_summary.csv` & `metrics/detector_outputs.csv` | **VERIFIED MATCH** |
| **Fig. 12: AC Power-Flow Numerical Consistency** | Title: *"Physical Protection & Control Governance Hierarchy"*. Plotted control governance categories. | **Title & Scope Corrected**: Title renamed to **"Fig. 12 — AC Power-Flow Numerical Consistency"**. Plotted quantities updated to machine double-precision active power loss conservation error $|\sum P_{\text{inj}} - \sum P_{\text{loss}}|$ across IEEE 9, 14, 30, 118 (bounded below $3.24 \times 10^{-14}$ p.u.). Y-axis labeled: *"AC Active Power Loss Conservation Error \|sum P_inj - sum P_loss\| (p.u.)"*. | `scripts/physical_sanity_check.py` | **VERIFIED MATCH** |

---

## 2. File Change Log

1. [`scripts/generate_paper_figures.py`](file:///c:/Users/burha/.gemini/antigravity/scratch/XMON-Grid/scripts/generate_paper_figures.py)  
   *(Updated `generate_fig2_k1_vs_k2_tradeoff` to plot 5-seed aggregate operating points with error bars, and updated `generate_fig12_physical_protection` to plot AC power-flow numerical consistency error across IEEE test beds.)*

2. `results/independent_validation_run/paper_figures/`  
   *(Regenerated `fig2_k1_vs_k2_tradeoff.pdf`/`.png` and `fig12_physical_protection.pdf`/`.png`.)*

3. [`results/independent_validation_run/paper_figures/FIGURE_MANIFEST.md`](file:///c:/Users/burha/.gemini/antigravity/scratch/XMON-Grid/results/independent_validation_run/paper_figures/FIGURE_MANIFEST.md)  
   *(Updated figure descriptions and source column details.)*

4. `results/independent_validation_run/paper_figures/SHA256SUMS.txt`  
   *(Updated SHA256 checksums for all 25 figure files.)*

5. [`docs/research_reset/PHASE_5G_FIGURE_AUDIT.md`](file:///c:/Users/burha/.gemini/antigravity/scratch/XMON-Grid/docs/research_reset/PHASE_5G_FIGURE_AUDIT.md)  
   *(Updated audit status table.)*

6. [`docs/research_reset/PHASE_5G_1_FIGURE_CORRECTION_AUDIT.md`](file:///c:/Users/burha/.gemini/antigravity/scratch/XMON-Grid/docs/research_reset/PHASE_5G_1_FIGURE_CORRECTION_AUDIT.md)  
   *(Created current figure correction audit report.)*

---

## 3. Final Verdict

### **FIGURES READY FOR MANUSCRIPT**
