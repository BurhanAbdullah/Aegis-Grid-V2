#!/bin/bash
DATA=$1
KEY=$2

echo "[ALPHA] Initiating 1000-layer recursive encapsulation..."
# This leverages the V3 recursive engine
ENCRYPTED=$(./v2_model/protocol/recursive_crypto.sh "$DATA" "$KEY")
./v2_model/protocol/matrix_stealth.sh "$ENCRYPTED"
echo "[ALPHA] Stealth Matrix populated."
