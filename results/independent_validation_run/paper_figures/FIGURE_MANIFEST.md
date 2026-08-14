# Figure Manifest: XMON-Grid Final Publication Figures

This manifest inventories all 12 IEEE Transactions publication figures generated in `results/independent_validation_run/paper_figures/`. Every figure is available in vector `.pdf` and 300 DPI `.png` format, generated directly from raw CSV source files.

---

## Master Figure Inventory

| Figure | Description | CSV Source File | Data Columns Used | $N$ (Samples) | Seeds | Data Match Verified |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Fig. 1** | Overall detection-performance comparison across 6 methods (F1, Recall, FPR) | `metrics/detector_outputs.csv` | `a_nis`, `a_cusum`, `a_jitter`, `a_seq`, `d_k2`, `y_true` | 1,200 | Primary (2026) | **VERIFIED MATCH** |
| **Fig. 2** | $K=1$ vs $K=2$ operating-point sensitivity trade-off (5-Seed Aggregates) | `tables/multi_seed_summary.csv` & `metrics/detector_outputs.csv` | $K=1$ OR-Gate (Rec=98.33%, FPR=57.92%), $K=2$ 5-Seed Aggregate (Rec=$85.85\pm 0.48\%$, FPR=$0.58\pm 0.73\%$) | 6,000 | 5 Seeds (2026--2030) | **VERIFIED MATCH** |
| **Fig. 3** | Receiver Operating Characteristic (ROC) curve ($\text{ROC-AUC} = 0.9771$) | `metrics/detector_outputs.csv` | `s_comp`, `y_true` | 1,200 | Primary (2026) | **VERIFIED MATCH** |
| **Fig. 4** | Precision–Recall (PR) curve ($\text{PR-AUC} = 0.9950$) | `metrics/detector_outputs.csv` | `s_comp`, `y_true` | 1,200 | Primary (2026) | **VERIFIED MATCH** |
| **Fig. 5** | Case-wise multi-seed mean F1 performance across IEEE 9/14/30/118 | `audit/audit_5seed_case_wise.csv` | `case`, `mean_F1`, `SD_F1` | 1,500 / case | 5 Seeds (2026--2030) | **VERIFIED MATCH** |
| **Fig. 6** | Attack-wise multi-seed mean F1 & Recall across 4 attack scenarios | `audit/audit_5seed_attack_wise.csv` | `scenario`, `mean_F1`, `SD_F1`, `mean_Recall`, `SD_Recall` | 1,200 / scenario | 5 Seeds (2026--2030) | **VERIFIED MATCH** |
| **Fig. 7** | Component ablation study (Full $K=2$ vs Ablations A--F) | `audit/audit_ablation_results.csv` | `Configuration`, `F1`, `FPR` | 1,200 | Primary (2026) | **VERIFIED MATCH** |
| **Fig. 8** | Log-scale false-positive rate vs sensitivity trade-off across methods | `comprehensive_comparison.csv` | `method`, `metric`, `value` | 1,200 | Primary (2026) | **VERIFIED MATCH** |
| **Fig. 9** | Measurement-noise robustness sweep ($\sigma_v \in [0.0005 .. 0.010]$ p.u.) | `robustness_results.csv` | `Exp5_Measurement_Noise_Sweep` (`param_value`, `F1`, `FPR`) | 1,200 / point | Seeds 2026, 2027 | **VERIFIED MATCH** |
| **Fig. 10** | Attack-severity spectrum robustness sweep (Tiers 1--4) | `robustness_results.csv` | `Exp4_Severity_Sweep` (`param_value`, `Recall`, `F1`) | 1,200 / tier | 5 Seeds (2026--2030) | **VERIFIED MATCH** |
| **Fig. 11** | Computational latency & empirical scaling fit ($O(N^{0.86}), R^2 = 0.8732$) | `robustness_results.csv` | `Exp9_Scalability_Latency` (`num_buses`, `per_step_latency_ms`) | Benchmark | IEEE 9--118 | **VERIFIED MATCH** |
| **Fig. 12** | AC power-flow numerical consistency ($|\sum P_{\text{inj}} - \sum P_{\text{loss}}| < 3.24 \times 10^{-14}$ p.u.) | `scripts/physical_sanity_check.py` | AC active power loss conservation error | 1,200 | IEEE 9--118 | **VERIFIED MATCH** |
