#!/usr/bin/env bash

set -e

echo "======================================"
echo "AEGIS-GRID-V2 FULL REPRODUCIBILITY PIPELINE"
echo "IEEE TRANSACTIONS VALIDATION SCRIPT"
echo "======================================"

echo ""
echo "Checking MATLAB installation..."

if command -v matlab &> /dev/null
then
    MATLAB_AVAILABLE=true
    echo "MATLAB detected ✓"
else
    MATLAB_AVAILABLE=false
    echo "MATLAB not detected."
    echo "Install MATLAB R2023b + MATPOWER 7.1 to execute simulations."
fi

echo ""
echo "Checking MATPOWER..."

if [ ! -d "matpower" ]; then
    echo "Downloading MATPOWER..."
    git clone https://github.com/MATPOWER/matpower.git
else
    echo "MATPOWER already present ✓"
fi

echo ""
echo "Preparing directories..."

mkdir -p results
mkdir -p figures
mkdir -p scripts

if [ "$MATLAB_AVAILABLE" = true ]; then

    echo ""
    echo "Running baseline experiments..."
    matlab -batch "addpath(genpath('matpower')); addpath(genpath('scripts')); run_baseline"

    echo ""
    echo "Running breaker-status topology attacks..."
    matlab -batch "addpath(genpath('matpower')); addpath(genpath('scripts')); run_attacks"

    echo ""
    echo "Running slow-drift topology attacks..."
    matlab -batch "addpath(genpath('matpower')); addpath(genpath('scripts')); run_slow_drift_attack"

    echo ""
    echo "Running impedance perturbation attacks..."
    matlab -batch "addpath(genpath('matpower')); addpath(genpath('scripts')); run_impedance_attack"

    echo ""
    echo "Running stealth topology attacks (no flooding)..."
    matlab -batch "addpath(genpath('matpower')); addpath(genpath('scripts')); run_stealth_attack"

    echo ""
    echo "Generating tables..."
    matlab -batch "addpath(genpath('scripts')); generate_tables"

    echo ""
    echo "Generating figures..."
    matlab -batch "addpath(genpath('scripts')); generate_figures"

else

    echo ""
    echo "Skipping MATLAB execution (environment check only)."

fi

echo ""
echo "======================================"
echo "PIPELINE COMPLETE"
echo "======================================"
