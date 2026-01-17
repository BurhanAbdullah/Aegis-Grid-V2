#!/bin/bash
DATA=$1
KEY=$2
LAYERS=1000
CURRENT_BLOB=$DATA
for ((i=1; i<=LAYERS; i++)); do
    CURRENT_BLOB=$(echo -n "$CURRENT_BLOB$KEY$i" | sha256sum | awk '{print $1}')
done
echo "$CURRENT_BLOB"
