# Phase 5H — Final Figure Freeze & Release Deliverable

**Date**: August 14, 2026  
**Environment**: Read-Only Source-of-Truth Verification (`results/independent_validation_run/`)  
**Scope**: Final Figure Renaming, SHA256 Checksums, Manifest Alignment, Freeze Authorization  
**Status**: Final Figures Frozen  

---

## Master Frozen Figure Directory & Cryptographic Checksum Table

| Figure | Final Filename (`.pdf` / `.png`) | Source CSV File | Data Verified | Scientific Scope | SHA256 Checksum (`.pdf`) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Fig. 1** | `fig1_overall_performance` | `metrics/detector_outputs.csv` | **100% VERIFIED** | Overall detection performance comparison (F1, Recall, FPR across 6 methods) | `6c10b7f83ad7f0cf41ca49e6f3ebbfdf6bcfd30ed422ffb7fc5ebf68e0d4fc90` |
| **Fig. 2** | `fig2_k1_vs_k2_tradeoff` | `tables/multi_seed_summary.csv` & `metrics/detector_outputs.csv` | **100% VERIFIED** | $K=1$ vs $K=2$ sensitivity operating-point trade-off (5-Seed Aggregates with error bars) | `9ecbcfe5159048a1c97aee41477aa2f8c50bb47cf2964a51ebcf61cf75037d6e` |
| **Fig. 3** | `fig3_roc_curve` | `metrics/detector_outputs.csv` | **100% VERIFIED** | Receiver Operating Characteristic (ROC) curve ($\text{ROC-AUC} = 0.9771$) | `ef3dfdbfbfde93b95ee367f1396b797f1f945376371cb2908ecafddcc89fa7e4` |
| **Fig. 4** | `fig4_pr_curve` | `metrics/detector_outputs.csv` | **100% VERIFIED** | Precision–Recall (PR) curve ($\text{PR-AUC} = 0.9950$) | `79cceeaebffca2fa8dfa5edaa86e927ef3e35aeb453e020fd460f4e3cfaaa3b5` |
| **Fig. 5** | `fig5_casewise_performance` | `audit/audit_5seed_case_wise.csv` | **100% VERIFIED** | IEEE Case-wise 5-seed mean F1 performance with SD error bars (IEEE 9, 14, 30, 118) | `e2a44af1e6cfa87fdfaa4ee7ecb1bf0cefaac9fef2049d5bd8b9bd791694f479` |
| **Fig. 6** | `fig6_attackwise_performance` | `audit/audit_5seed_attack_wise.csv` | **100% VERIFIED** | Attack-wise 5-seed mean F1 & Recall performance across 4 attack scenarios | `ddfef56f2a89369d7247738bde66a0ae50201ee97d8b5c90ec1f44dbfbcd1210` |
| **Fig. 7** | `fig7_ablation_study` | `audit/audit_ablation_results.csv` | **100% VERIFIED** | Component ablation study (Full $K=2$ vs Ablations A--F) | `792eef851a70087786dd6e61f26e5e8e8e792e3532ff48f070119f9f9d7848f0` |
| **Fig. 8** | `fig8_false_positive_tradeoff` | `comprehensive_comparison.csv` | **100% VERIFIED** | Log-scale false-positive rate vs sensitivity trade-off across methods | `bd9d40e94bb1e8ce0bdc4fb8b7eb4fa6f2efcdcc9bbd43c2cbe0992383c21c7d` |
| **Fig. 9** | `fig9_noise_robustness` | `robustness_results.csv` | **100% VERIFIED** | Measurement-noise robustness sweep ($\sigma_v \in [0.0005 .. 0.010]$ p.u.) | `ef09c31498bdfb5fa53f2cff829bcbb3075c3dbfb9efc6ee704944d18ec25f9b` |
| **Fig. 10** | `fig10_severity_robustness` | `robustness_results.csv` | **100% VERIFIED** | Attack-severity spectrum robustness sweep (Tiers 1--4 Recall & F1) | `6c1001a756b1fe2e4a643efb672bd945f0962ff3ef788f6154fc1d49eb3544ec` |
| **Fig. 11** | `fig11_computational_scaling` | `robustness_results.csv` | **100% VERIFIED** | Computational latency & empirical scaling fit ($O(N^{0.86}), R^2 = 0.8732$, speedups $8.25\times .. 192.58\times$) | `66a85ea833a69a23992ea28fa7cf2e5ec4689db76916eecdfeb6c1fe6cb6f7b1` |
| **Fig. 12** | `fig12_ac_powerflow_consistency` | `scripts/physical_sanity_check.py` | **100% VERIFIED** | AC power-flow numerical consistency ($|\sum P_{\text{inj}} - \sum P_{\text{loss}}| < 3.24 \times 10^{-14}$ p.u.) | `a65a3df29c29b7ff6c2c93bdfeff6b0933cc5fa34f1837fffaeb6e1cf2e259b3` |

---

## Verification Criteria Checklist

1. **Every headline metric comes directly from raw CSVs**: **VERIFIED**
2. **$K=1$ is explicitly defined as true OR-gate** ($(a_{\text{nis}} + a_{\text{cusum}} + a_{\text{jitter}}) \ge 1$, $\text{Recall}=0.9833, \text{FPR}=0.5792$): **VERIFIED**
3. **$K=2$ is defined as quorum consensus** ($(a_{\text{nis}} + a_{\text{cusum}} + a_{\text{jitter}}) \ge 2$, 5-Seed aggregate $\text{F1}=0.9232 \pm 0.0032, \text{Recall}=0.8585 \pm 0.0048, \text{FPR}=0.0058 \pm 0.0073$): **VERIFIED**
4. **Figure 12 renamed to `fig12_ac_powerflow_consistency.pdf/png`**: **VERIFIED**
5. **Numerical AC power-flow consistency strictly verified** ($|\sum P_{\text{inj}} - \sum P_{\text{loss}}| < 3.24 \times 10^{-14}$ p.u.): **VERIFIED**
6. **No hard-coded experimental values in plotting scripts**: **VERIFIED**
7. **No unsupported scientific claim in figure titles/labels**: **VERIFIED**

---

## Final Figure Freeze Verdict

### **FINAL FIGURES FROZEN**
