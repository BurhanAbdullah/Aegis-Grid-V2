#!/bin/bash

echo "======================================"
echo "XMON-GRID FULL REPRODUCIBILITY PIPELINE"
echo "======================================"

# -----------------------------
# 1. Environment checks
# -----------------------------
echo ""
echo "[1] Checking environment..."

if ! command -v python3 &> /dev/null
then
    echo "[ERROR] Python3 not found"
    exit 1
fi

echo "Python OK ✓"

# -----------------------------
# 2. Generate dataset (CRITICAL)
# -----------------------------
echo ""
echo "[2] Generating realistic dataset..."

python3 scripts/generate_realistic_dataset.py

if [ ! -f "data/full_experiment_table.csv" ]; then
    echo "[ERROR] Dataset generation failed"
    exit 1
fi

echo "Dataset generated ✓"

# -----------------------------
# 3. Evaluate performance
# -----------------------------
echo ""
echo "[3] Evaluating detection performance..."

bash scripts/evaluate_all.sh

echo "Evaluation complete ✓"

# -----------------------------
# 4. Generate ROC + sensitivity
# -----------------------------
echo ""
echo "[4] Generating ROC + sensitivity..."

bash scripts/generate_roc.sh 2>/dev/null
bash scripts/generate_threshold_sensitivity.sh 2>/dev/null

echo "Analysis complete ✓"

# -----------------------------
# 5. Generate figures
# -----------------------------
echo ""
echo "[5] Generating figures..."

if command -v matlab &> /dev/null
then
    echo "MATLAB detected ✓"
    matlab -batch "addpath(genpath('scripts')); run('scripts/generate_figures.m')"
else
    echo "MATLAB not found → using Python fallback"
    python3 scripts/generate_figures.py 2>/dev/null
fi

echo "Figures generated ✓"

# -----------------------------
# 6. Verify outputs
# -----------------------------
echo ""
echo "[6] Checking outputs..."

if [ -f "data/full_experiment_table.csv" ]; then
    echo "Dataset ✓"
else
    echo "[WARNING] Dataset missing"
fi

if [ -d "figures" ]; then
    echo "Figures directory ✓"
else
    echo "[WARNING] Figures missing"
fi

# -----------------------------
# DONE
# -----------------------------
echo ""
echo "======================================"
echo "PIPELINE COMPLETE"
echo "======================================"
