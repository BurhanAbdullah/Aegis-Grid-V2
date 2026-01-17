#!/bin/bash
# Aegis-Grid Multi-Version Controller
export PYTHONPATH=$PYTHONPATH:.

case "$1" in
    v2-audit)
        echo "[INFO] Running V2 Master (Adaptive CAP)..."
        python3 -m v2_model.tests.stress.full_audit
        ;;
    v3-evolve)
        echo "[INFO] Running V3 Morphic (Causal Logic)..."
        ./v3_fabric/fabric.sh evolve
        ;;
    v4-consensus)
        echo "[INFO] Running V4 Hive (Tri-Agent Consensus)..."
        ./v4_hive/gate/hive_gate.sh "SECURE_DATA" "KEY_1000L"
        ;;
    push)
        git add .
        git commit -m "RESEARCH_SYNC: V2 Stable with V3/V4 Experimental Substrates"
        git push origin main
        ;;
    *)
        echo "Usage: ./manage.sh {v2-audit|v3-evolve|v4-consensus|push}"
        ;;
esac
