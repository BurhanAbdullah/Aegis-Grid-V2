#!/bin/bash
REAL_DATA_HEX=$1
MATRIX_SIZE=1000
MATRIX_FILE="v3_fabric/synapses/data_matrix.bin"
mkdir -p v3_fabric/synapses
head -c $((32 * MATRIX_SIZE)) /dev/urandom > "$MATRIX_FILE"
OFFSET=$(( ( RANDOM % MATRIX_SIZE ) * 32 ))
echo -n "$REAL_DATA_HEX" | dd of="$MATRIX_FILE" bs=1 seek="$OFFSET" conv=notrunc 2>/dev/null
