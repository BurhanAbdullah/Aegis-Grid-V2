#!/bin/bash
set -e

echo '[1/6] Environment validation'
python3 validation/validate_env.py

echo '[2/6] Dataset generation'
python3 scripts/generate_data.py

echo '[3/6] Experiment execution'
python3 scripts/run_experiments.py

echo '[4/6] Figure generation'
python3 scripts/generate_figures.py

echo '[5/6] Result validation'
python3 validation/validate_results.py

echo '[6/6] Pipeline complete'
