#!/bin/bash
set -e
export PYTHONPATH="$(pwd)"

echo "[AUDIT] Running Aegis-Grid V2 Full Verification"
python3 -m v2_model.tests.stress.full_audit
echo "[AUDIT] SUCCESS"
