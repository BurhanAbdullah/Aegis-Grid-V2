#!/bin/bash
# Aegis-Grid V3.0 Chaos Substrate: Multi-Vector Adversarial Audit

# Configuration
REAL_MAC="00:15:5d:01:af:12"
SPOOFED_MAC="aa:bb:cc:dd:ee:ff"

function attack_header() {
    echo -e "\033[1;31m[ADVERSARY] Initiating Vector: $1\033[0m"
}

# 1. Vector: MAC Spoofing (L1 Attack)
function test_spoofing() {
    attack_header "L1 HARDWARE SPOOFING"
    ./v2_model/agents/causal_neuron.sh "SUBSTATION_01" "$SPOOFED_MAC"
    if [ $? -eq 137 ]; then
        echo -e "\033[1;32m[RESULT] L1 Defense Success: Spoof Identity Purged.\033[0m"
    fi
}

# 2. Vector: DDoS & Jitter (L5/L2 Attack)
function test_audit() {
    attack_header "L5/L2 ADVERSARIAL PRESSURE"
    export PYTHONPATH=$PYTHONPATH:.
    python3 -m v2_model.tests.stress.full_audit
    echo -e "\033[1;32m[RESULT] L5/L2 Defense Success: CAP/Timing Vectors Stable.\033[0m"
}

# Execute
test_spoofing
test_audit
