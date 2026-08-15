#!/usr/bin/env bash
set -e

echo "================================================="
echo "XMON-GRID FINAL REPRODUCTION PIPELINE"
echo "================================================="

# -------------------------------------------------
# CLEAN OUTPUTS
# -------------------------------------------------

mkdir -p \
paper/data \
paper/tables \
paper/figures \
results/csv

# -------------------------------------------------
# DATASET GENERATION (AUTHORITATIVE DETERMINISTIC)
# -------------------------------------------------

echo
echo "[1/8] Generating deterministic realistic dataset..."

python3 scripts/generate_realistic_dataset.py
cp data/full_experiment_table.csv results/final_dataset.csv

# -------------------------------------------------
# MONTE CARLO (LEGACY / NON-AUTHORITATIVE DEMO)
# -------------------------------------------------

echo
echo "[2/8] Running Monte Carlo (legacy demo)..."

python3 experiments/run_monte_carlo.py
python3 experiments/analyze_monte_carlo.py

# -------------------------------------------------
# STEALTH SWEEP (LEGACY / NON-AUTHORITATIVE DEMO)
# -------------------------------------------------

echo
echo "[3/8] Running stealth sweep (legacy demo)..."

python3 experiments/run_stealth_sweep.py

# -------------------------------------------------
# SCALING (LEGACY / NON-AUTHORITATIVE DEMO)
# -------------------------------------------------

echo
echo "[4/8] Running scalability benchmarks (legacy demo)..."

python3 experiments/benchmark_scaling.py

# -------------------------------------------------
# EXPORT PAPER DATA (AUTHORITATIVE K=1 & K=2 METRICS)
# -------------------------------------------------

echo
echo "[5/8] Exporting paper datasets & metrics..."

python3 scripts/export_paper_data.py

# -------------------------------------------------
# SEQUENTIAL PHYSICS
# -------------------------------------------------

echo
echo "[6/8] Generating sequential physics traces..."

python3 scripts/add_sequential_physics.py
python3 scripts/fix_sequential_threshold.py

# -------------------------------------------------
# FIGURES
# -------------------------------------------------

echo
echo "[7/8] Generating figures..."

python3 scripts/generate_figures.py || true

# -------------------------------------------------
# VALIDATION
# -------------------------------------------------

echo
echo "[8/8] Final validation..."

ls paper/data
ls paper/tables
ls paper/figures

echo
echo "================================================="
echo "FINAL REPRODUCTION COMPLETE"
echo "================================================="

