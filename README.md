# AEGIS-Grid V2

Reproducibility repository for:

## Cyber-Physical Detection of Coordinated Topology and Timing Attacks in Smart-Grid SCADA Systems

## Overview

AEGIS-Grid V2 is a cyber-physical anomaly detection framework for smart-grid security evaluation under coordinated false-data injection and topology manipulation attacks.

The framework integrates:

- Sequential innovation monitoring
- Adaptive CUSUM analysis
- Jacobian conditioning analysis
- Timing anomaly detection
- Byzantine consensus validation
- MATPOWER AC power-flow validation

## Repository Structure

paper/              LaTeX manuscript  
plotting_data/      CSV datasets for figures/tables  
scripts/            Reproducibility scripts  
matpower/           MATPOWER validation pipeline  
results/            Generated outputs  
figures/            Generated figures  

## Requirements

- Python 3.11+
- MATLAB or GNU Octave
- MATPOWER 7.1+

Install dependencies:

pip install -r requirements.txt

## Reproducibility

Run all experiments:

bash scripts/run_all.sh

Verify outputs:

bash scripts/verify_paper_results.sh

## Outputs

The pipeline regenerates:

- ROC curves
- Threshold sensitivity analysis
- Sequential detector outputs
- MATPOWER cyber-physical datasets
- Timing anomaly datasets
- Final plotting CSV files

## License

MIT License
