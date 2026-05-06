#!/usr/bin/env bash
set -e

echo "=============================================="
echo " AEGIS-GRID V2 MASTER VERIFICATION (V2.1 / V3 / V4)"
echo "=============================================="

# --- Environment sanity ---
if [[ -z "$VIRTUAL_ENV" ]]; then
  echo "[ERROR] Virtual environment not active"
  exit 1
fi

echo "[OK] Python: $(python --version)"

# --- Ensure repo root is on PYTHONPATH ---
export PYTHONPATH="$(pwd)"

# -------------------------------
# V2.1 — Stable Substrate
# -------------------------------
echo ""
echo ">>> VERIFYING V2.1 (STABLE SUBSTRATE)"
python verify_everything.py
echo "[PASS] V2.1 core verification complete"

# -------------------------------
# V3 — Morphic / Causal Fabric
# -------------------------------
echo ""
echo ">>> VERIFYING V3 (MORPHIC FABRIC)"
if [[ -d "v3_fabric" ]]; then
  bash chaos_test.sh
  echo "[PASS] V3 chaos / morphic verification complete"
else
  echo "[SKIP] V3 fabric not present"
fi

# -------------------------------
# V4 — Hive Consensus
# -------------------------------
echo ""
echo ">>> VERIFYING V4 (HIVE CONSENSUS)"
if [[ -d "v4_hive" ]]; then
  bash stress_audit.sh
  echo "[PASS] V4 hive stress verification complete"
else
  echo "[SKIP] V4 hive not present"
fi

# -------------------------------
# Forensic confirmation
# -------------------------------
echo ""
echo ">>> CHECKING FORENSIC ARCHIVE"
if [[ -d "final_archive" ]]; then
  echo "[OK] Forensic artifacts stored in final_archive/"
else
  echo "[WARN] final_archive missing"
fi

echo ""
echo "=============================================="
echo " AEGIS-GRID V2 VERIFICATION STATUS: GREEN"
echo "=============================================="
