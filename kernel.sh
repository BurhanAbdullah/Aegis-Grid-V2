#!/bin/bash
# Aegis-Grid V2.0 Kernel Manager

export PYTHONPATH=$PYTHONPATH:.

function run_substrate_audit() {
    echo -e "\033[1;34m[KERNEL] Engaging V2 Intelligence Substrate...\033[0m"
    # Execute the audit which uses the Cognitive Agent to reason about stress
    python3 -m v2_model.tests.stress.full_audit
}

function view_forensics() {
    echo -e "\033[1;36m[KERNEL] Extracting Agent Reasoning Path...\033[0m"
    cat v2_model/logs/audit_trail.log | tail -n 20
}

case "$1" in
    audit) run_substrate_audit ;;
    logs)  view_forensics ;;
    push)
        git add .
        git commit -m "V2_SUBSTRATE: Cognitive Agent & Actuator Stack Deployed"
        git push origin main
        ;;
    *) echo "Usage: ./kernel.sh {audit|logs|push}" ;;
esac
