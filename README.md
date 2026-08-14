<p align="center">
  <img src="banner.png" width="100%" alt="XMON-Grid Banner"/>
</p>

# XMON-Grid

## Sequential Innovation Accumulation and Cross-Layer Quorum Consensus for Topology-Attack Detection in SCADA-Monitored Transmission Systems

Official research implementation and reproducible evaluation framework accompanying the manuscript:

> **Sequential Innovation Accumulation and Cross-Layer Quorum Consensus for Topology-Attack Detection in SCADA-Monitored Transmission Systems**

---

## Overview

XMON-Grid introduces a physical-statistical anomaly detection and multi-detector quorum voting framework designed for transmission grid cyber-physical security. The proposed method monitors SCADA telemetry timing integrity and physical state estimation residuals to detect coordinated topology manipulation, False Data Injection Attacks (FDIA), branch outages, load shift manipulations, and stealth drift attacks.

The framework integrates three complementary sub-detector streams:
- **Physical State Estimation Residuals:** Normalized Innovation Squared ($\text{NIS}$) derived from dynamic Extended Kalman Filtering (EKF).
- **Statistical Drift Monitoring:** Adaptive Page–Hinkley Cumulative Sum ($\text{CUSUM}$) tracking of low-amplitude residual shifts.
- **Communication-Layer Timing Monitoring:** Packet arrival timing jitter statistics ($J$) detecting telemetry network manipulation.

Sub-detector outputs are integrated using a multi-agent voting quorum framework establishing both a primary conservative operating point ($K=2$ Consensus Quorum) and a secondary high-sensitivity operating point ($K=1$ Sensitivity OR-Gate Mode).

---

## Benchmark Evaluation Scope & Authoritative Results

The framework is evaluated across four IEEE transmission network benchmark topologies (IEEE 9, IEEE 14, IEEE 30, and IEEE 118 bus systems) under five operational conditions (`baseline`, `branch_outage`, `fdia`, `load_shift`, and `stealth_drift`).

Evaluations are conducted using five independent random seeds (Seeds 2026–2030) spanning $N=6,000$ total test evaluations ($N=1,200$ test evaluations per seed; $1,500$ evaluations per grid case).

State estimation, Jacobian calculations, and physical AC power-flow simulations were executed directly via `pandapower` and `PyPSA` Python APIs. (The PowerMCP RPC daemon was not invoked during experimental evaluations).

### Authoritative 5-Seed Independent Validation Summary (`results/independent_validation_run/`):

| Operating Mode / Method | F1-Score | Recall | False Positive Rate (FPR) | MCC | ROC-AUC / PR-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **$K=2$ Quorum Mode (5-Seed Aggregate Mean $\pm$ SD)** | **$0.9232 \pm 0.0032$** | **$0.8585 \pm 0.0048$** | **$0.0058 \pm 0.0073$** ($< 0.6\%$) | **$0.7362 \pm 0.0100$** | N/A (Discrete Quorum) |
| **$K=1$ Sensitivity Mode (True OR-Gate)** | **$0.8847$** | **$0.9833$** ($98.33\%$) | **$0.5792$** ($57.92\%$) | **$0.5054$** | N/A (Discrete OR-Gate) |
| **Continuous Threat Score ($S_{\text{comp}}$)** | N/A | N/A | N/A | N/A | **ROC-AUC = $0.9771$ / PR-AUC = $0.9950$** |
| **NIS Standalone** | $0.8550 \pm 0.0064$ | $0.7467 \pm 0.0089$ | $0.0058 \pm 0.0073$ | $0.6274 \pm 0.0112$ | N/A |
| **CUSUM Standalone** | $0.9866 \pm 0.0012$ | $0.9733 \pm 0.0024$ | $0.0000 \pm 0.0000$ | $0.9634 \pm 0.0031$ | N/A |
| **Jitter Standalone** | $0.2407 \pm 0.0000$ | $0.1367 \pm 0.0000$ | $0.0000 \pm 0.0000$ | $0.2023 \pm 0.0000$ | N/A |

### IEEE Case-Wise Performance ($K=2$ Quorum Mode):
- **IEEE 9-bus**: Mean F1 = $0.9215 \pm 0.0075$, Mean Recall = $0.8567$, Mean FPR = $0.0100$
- **IEEE 14-bus**: Mean F1 = $0.9163 \pm 0.0055$, Mean Recall = $0.8483$, Mean FPR = $0.0133$
- **IEEE 30-bus**: Mean F1 = $0.9261 \pm 0.0062$, Mean Recall = $0.8625$, Mean FPR = $0.0000$
- **IEEE 118-bus**: Mean F1 = $0.9286 \pm 0.0015$, Mean Recall = $0.8667$, Mean FPR = $0.0000$

### Computational Complexity & Measured Speedups:
Vectorized NumPy measurement and analytical Jacobian calculations achieve an empirical execution speedup ranging from **$8.25\times$** (IEEE 9) to **$192.58\times$** (IEEE 118) over scalar Python loops. The measurement and Jacobian engine exhibits $O(N^{0.86})$ scaling ($\ln t = 0.8641 \ln N - 5.0302, R^2 = 0.8732$). Full EKF Kalman gain matrix inversion $(3N \times 3N)$ scales separately as $O(N^{2.3})$.

---

## Quick Start & Reproduction

### 1. Installation & Environment Setup
```bash
git clone https://github.com/BurhanAbdullah/XMON-Grid.git
cd XMON-Grid
pip install -r requirements.txt
```

### 2. Run Automated Verification & Unit Tests
```bash
# Run unit test suite
python -m unittest discover tests

# Verify double-precision AC power-flow conservation (|sum P_inj - sum P_loss| < 3.24e-14 p.u.)
python scripts/physical_sanity_check.py
```

### 3. Reproduce Independent Validation & Figures
To execute the complete 5-seed independent experiment runner and regenerate all publication figures:

```bash
# Execute independent 5-seed validation suite (Seeds 2026-2030)
python scripts/run_independent_validation.py

# Generate all 12 IEEE Transactions publication figures (.pdf and .png)
python scripts/generate_paper_figures.py

# Verify SHA256 checksums of generated figures
python scripts/generate_figure_checksums.py
```

Generated datasets, metric tables, and publication figures are stored in `results/independent_validation_run/`.

---

## Repository Structure

```text
XMON-Grid/
├── README.md                              # Master repository guide & evaluation summary
├── LICENSE                                # MIT License
├── requirements.txt                       # Python dependencies
├── banner.png                             # Project header graphic
├── core/                                  # AUTHORITATIVE MODEL IMPLEMENTATION
│   ├── xmon_model.py                      # EKF, CUSUM, Jitter, Quorum Logic
│   ├── grid_topology.py                   # Vectorized Ybus, h(x), H(x) Engine
│   ├── data_pipeline.py                   # Physical AC Power Flow & Datasets
│   └── consensus.py                       # Quorum Voting & Aggregation
├── scripts/                               # REPRODUCIBILITY & VALIDATION TOOLING
│   ├── run_independent_validation.py      # Independent 5-Seed Runner (Seeds 2026-2030)
│   ├── run_phase5e_robustness.py          # 11 Robustness Parameter Sweeps Runner
│   ├── perform_deep_validation_audit.py   # Metric & McNemar Audit Script
│   ├── perform_phase5i_forensic_gate.py   # Pre-Submission Forensic Auditor
│   ├── generate_paper_figures.py          # IEEE Transactions Figure Generator (Figs 1-12)
│   ├── generate_figure_checksums.py       # SHA256 Checksum Generator
│   └── physical_sanity_check.py           # Power Flow Conservation Verifier
├── tests/                                 # AUTOMATED TEST SUITE
│   └── test_xmon_model.py                 # Core Model Unit Tests (16 tests, 100% pass)
├── results/                               # EXPERIMENTAL RESULTS STORE
│   ├── independent_validation_run/        # AUTHORITATIVE: Phase 5 Multi-Seed Run (Seeds 2026-2030)
│   │   ├── metrics/                       # Raw Sample Predictions (detector_outputs.csv)
│   │   ├── tables/                        # Multi-Seed Summaries (multi_seed_summary.csv)
│   │   ├── audit/                         # 6 Audit CSV Tables (Case-wise, Attack-wise, McNemar)
│   │   ├── comprehensive_comparison.csv   # Comprehensive Baseline & Ablation Comparison
│   │   ├── robustness_results.csv         # Parameter Sweeps Dataset
│   │   └── paper_figures/                 # 12 Frozen Figures (.pdf & .png, Manifest, SHA256SUMS)
│   ├── tsg_run_002/                       # HISTORICAL: Frozen Reference Run (Seed 42)
│   └── tsg_run_001/                       # HISTORICAL: Initial Prototype Run (N=960)
├── docs/                                  # RESEARCH DOCUMENTATION & AUDIT TRAIL
│   └── research_reset/                    # Phase 5 Authoritative Audit Reports
├── paper/                                 # LATEX MANUSCRIPT DIRECTORY
│   └── main.tex                           # Main LaTeX Source File
└── archive/                               # HISTORICAL ARCHIVE
    ├── historical_results/                # Legacy result text files
    ├── legacy_scripts/                    # Legacy shell drivers (run_all.sh, verify_paper_results.sh)
    └── legacy_experiments/                # Legacy prototype experiment drivers
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
