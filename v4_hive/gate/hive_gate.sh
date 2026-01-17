#!/bin/bash
# V4.0 HIVE-GATE: CONSENSUS-BASED DECRYPTION

function release_data() {
    # 1. Run Protector
    ./v4_hive/chamber_alpha/protector.sh "$1" "$2"
    
    # 2. Check Beta (Identity)
    ./v4_hive/chamber_beta/auditor.sh "00:15:5d:01:af:12" "CERT_PQ_VAL"
    BETA_SIG=$?
    
    # 3. Check Gamma (Compliance)
    ./v4_hive/chamber_gamma/monitor.sh
    GAMMA_SIG=$?
    
    # 4. Final Consensus
    if [ $BETA_SIG -eq 0 ] && [ $GAMMA_SIG -eq 0 ]; then
        echo -e "\033[1;32m[HIVE-GATE] CONSENSUS REACHED. Data Integrity Secured.\033[0m"
        echo "[ACTION] Moving data to Decryption Keyhole."
    else
        echo -e "\033[1;31m[HIVE-GATE] CONSENSUS FAILED. Initiating Data Self-Destruction.\033[0m"
        rm -rf v3_fabric/synapses/data_matrix.bin
    fi
}

release_data "$1" "$2"
