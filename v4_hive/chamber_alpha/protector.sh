#!/bin/bash
# AGENT ALPHA: DATA ENCAPSULATION & MATRIX STEALTH
DATA=$1
KEY=$2

echo "[ALPHA] Encapsulating in 1000-layers. Generating Matrix..."
# Call the recursive engine and matrix injector
ENCRYPTED=$(./v2_model/protocol/recursive_crypto.sh "$DATA" "$KEY")
./v2_model/protocol/matrix_stealth.sh "$ENCRYPTED"
echo "[ALPHA] Data Hidden. Offset transmitted to Hive-Gate."
