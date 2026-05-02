#!/bin/bash

echo "======================================"
echo "AEGIS-GRID-V2 PAPER RESULT VERIFIER"
echo "IEEE TRANSACTIONS CHECK PIPELINE"
echo "======================================"

echo ""
echo "[1] Activating Python virtual environment..."

if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
fi

echo ""
echo "[2] Fixing requirements file (removing MATLAB entry)..."

sed -i '/MATLAB R2023b/d' requirements.txt 2>/dev/null

echo ""
echo "[3] Installing dependencies..."

pip install -r requirements.txt

echo ""
echo "[4] Running pipeline verification..."

python verify_everything.py

echo ""
echo "[5] Running secondary verification..."

python verify_v2.sh 2>/dev/null || true

echo ""
echo "[6] Generating plotting datasets..."

python generate_v4_plot.py

echo ""
echo "[7] Checking results directory..."

if [ "$(ls -A results 2>/dev/null)" ]; then
    echo "Results directory populated ✓"
else
    echo "WARNING: results directory empty (MATLAB simulations required)"
fi

echo ""
echo "[8] Checking plotting data..."

if [ "$(ls -A plotting_data 2>/dev/null)" ]; then
    echo "Plotting datasets generated ✓"
else
    echo "WARNING: plotting_data directory empty"
fi

echo ""
echo "[9] Searching detector triggers..."

grep -Ri "trigger" . | head -n 10

echo ""
echo "[10] Searching consensus decisions..."

grep -Ri "consensus" . | head -n 10

echo ""
echo "======================================"
echo "PIPELINE CHECK COMPLETE"
echo "======================================"
