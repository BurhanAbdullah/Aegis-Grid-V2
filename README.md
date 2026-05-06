# AEGIS-Grid V2

Implementation and evaluation code accompanying the paper:

## Sequential Innovation and Cross-Layer Consensus Monitoring for Coordinated Topology and Timing Attack Detection in Smart Grids

---

## Overview

AEGIS-Grid V2 implements cross-layer sequential anomaly-detection methodology for coordinated cyber-physical attack detection under AC power-flow constraints
The implementation integrates:

- Sequential innovation accumulation
- Adaptive Page--Hinkley CUSUM monitoring
- Jacobian conditioning analysis
- Timing-jitter anomaly statistics
- Authenticated consensus fusion
- MATPOWER AC power-flow validation

within MATPOWER-based AC power-flow simulations spanning IEEE benchmark transmission networks.

---

## Repository Structure

paper/              Manuscript sources and figures
plotting_data/      CSV datasets used for plots and tables
scripts/            Experiment and evaluation scripts
matpower/           MATPOWER validation pipeline
results/            Generated detector outputs
experiments/        Sequential and cross-layer evaluations

---

## Requirements

- Python 3.11+
- MATLAB or GNU Octave
- MATPOWER 7.1+

Install dependencies:

pip install -r requirements.txt

---

## Running Experiments

Run the complete evaluation pipeline:

bash scripts/run_all.sh

Verify generated outputs:

bash scripts/verify_paper_results.sh

---

## Generated Outputs

The pipeline regenerates:

- ROC curves
- Threshold-sensitivity analysis
- Sequential detector statistics
- MATPOWER cyber--physical datasets
- Timing anomaly datasets
- Cross-layer consensus outputs
- Plotting CSV files

---

## License

MIT License
