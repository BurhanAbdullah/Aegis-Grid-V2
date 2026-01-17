#!/bin/bash
# Aegis-Grid V3.0: Morphic Fabric Controller (The Nervous System)

MAC_ADDR="00:15:5d:01:af:12" # Targeted Substrate

function heart_beat() {
    ./v2_model/agents/causal_neuron.sh "SUBSTATION_01" "$MAC_ADDR"
    SIGNAL=$?

    if [ $SIGNAL -eq 1 ]; then
        echo -e "\033[0;35m[NEURON] Adversarial Intent Detected. Triggering Mutation...\033[0m"
        ./v2_model/protocol/morph.sh mutate
    elif [ $SIGNAL -eq 137 ]; then
        echo -e "\033[0;31m[NEURON] Hardware Breach. System Locked.\033[0m"
        exit 1
    else
        echo -e "\033[0;32m[NEURON] Fabric Stable.\033[0m"
    fi
}

# Run the evolutionary loop
while true; do
    heart_beat
    sleep 2
done
