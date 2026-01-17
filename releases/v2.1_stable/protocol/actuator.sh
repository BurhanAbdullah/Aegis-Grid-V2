#!/bin/bash
# V2.1: 8-Block Shuffle Actuator
DATA=$1
echo "[V2.1] Shuffling packet in 8-block Shannon window..."
./v2_model/protocol/matrix_stealth.sh "$DATA" 8
