#!/bin/bash

echo "======================================"
echo "AEGIS-GRID PAPER RESULT SUMMARY"
echo "Extracting usable results for manuscript"
echo "======================================"

echo ""
echo "[1] Checking plotting datasets..."

if [ -d plotting_data ]; then
    echo "plotting_data directory exists ✓"
    ls plotting_data
else
    echo "plotting_data directory missing"
fi


echo ""
echo "[2] Checking results directory..."

if [ -d results ]; then
    echo "results directory exists ✓"
    ls results
else
    echo "results directory missing"
fi


echo ""
echo "[3] Extracting detector threshold parameters..."

grep -Ri "eta_sigma" . | head -n 5
grep -Ri "kappa" . | head -n 5
grep -Ri "h_xi" . | head -n 5


echo ""
echo "[4] Extracting latency references..."

grep -Ri "latency" . | head -n 10


echo ""
echo "[5] Extracting trigger evidence..."

grep -Ri "triggered" . | head -n 10


echo ""
echo "[6] Extracting consensus logic evidence..."

grep -Ri "consensus" . | head -n 10


echo ""
echo "[7] Searching ROC-ready signals..."

grep -Ri "threshold" plotting_data 2>/dev/null | head -n 10


echo ""
echo "[8] Searching sequential detector outputs..."

grep -Ri "CUSUM" . | head -n 10
grep -Ri "NIS" . | head -n 10


echo ""
echo "[9] Searching IEEE test-system references..."

grep -Ri "ieee9" . | head -n 5
grep -Ri "ieee14" . | head -n 5
grep -Ri "ieee30" . | head -n 5
grep -Ri "ieee118" . | head -n 5


echo ""
echo "======================================"
echo "SUMMARY COMPLETE"
echo "======================================"
