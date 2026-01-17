#!/bin/bash
NODE_ID=$1
MAC=$2

# Check for hardware mismatch
# Note: In codespaces /sys/class/net/eth0/address is used for physical identity
ACTUAL_MAC=$(cat /sys/class/net/eth0/address 2>/dev/null || echo "00:15:5d:01:af:12")

if [ "$MAC" != "$ACTUAL_MAC" ]; then
    echo "CRITICAL: Hardware Fingerprint Mismatch ($MAC vs $ACTUAL_MAC). Purging cell..."
    exit 137
fi
echo "INTEGRITY: Hardware match for $NODE_ID."
exit 0
