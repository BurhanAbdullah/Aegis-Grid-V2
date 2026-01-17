#!/bin/bash

# Aegis-Grid V2.0 System Manager
# Proprietary Build: Jan 2026

case "$1" in
    setup)
        echo "[INFO] Configuring system dependencies..."
        python3 -m pip install matplotlib > /dev/null
        mkdir -p v2_model/logs v2_model/plots v2_model/telemetry
        export PYTHONPATH=$PYTHONPATH:.
        echo "[SUCCESS] Environment Initialized."
        ;;
    audit)
        echo "[INFO] Executing 7-Layer Adversarial Simulation..."
        export PYTHONPATH=$PYTHONPATH:.
        python3 -m v2_model.tests.stress.full_audit
        ;;
    clean)
        echo "[INFO] Purging cache and forensic logs..."
        find . -name "__pycache__" -type d -exec rm -rf {} +
        rm -rf v2_model/logs/*.log
        ;;
    push)
        echo "[INFO] Syncing with Private Vault..."
        git add .
        git commit -m "RESEARCH_UPDATE: Finalized 7-Layer Verified Stack"
        git push origin main
        ;;
    *)
        echo "Valid commands: setup, audit, clean, push"
        exit 1
        ;;
esac
