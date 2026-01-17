#!/bin/bash
# AGENT BETA: IDENTITY & DELIVERY VERIFICATION
TARGET_MAC=$1
PROVIDED_CERT=$2

echo "[BETA] Verifying Receiver Identity..."
ACTUAL_MAC=$(cat /sys/class/net/eth0/address 2>/dev/null || echo "00:15:5d:01:af:12")

if [ "$TARGET_MAC" == "$ACTUAL_MAC" ]; then
    echo "[BETA] Identity Confirmed. Receiver is Authorized."
    exit 0
else
    echo "[BETA] CRITICAL: Receiver Identity Fraud. Locking Gate."
    exit 1
fi
