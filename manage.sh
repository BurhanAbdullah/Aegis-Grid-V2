#!/bin/bash
export PYTHONPATH=$(pwd)

case "$1" in
    deploy-v2.1)
        echo "Deploying Aegis-Grid V2.1: Stable Substrate"
        ./releases/v2.1_stable/protocol/actuator.sh "GRID_DATA"
        ;;
    deploy-v4.0)
        echo "Deploying Aegis-Grid V4.0: Hive-Cell Consensus"
        ./releases/v4.0_hive_cell/protocol/actuator.sh "GRID_DATA" "VAULT_KEY_ALPHA"
        ;;
    audit-all)
        echo "Performing Multi-Tier Integrity Check..."
        sha256sum -c security_manifests/V2_INTEGRITY_MANIFEST.sha256
        ;;
    push)
        git add .
        git commit -m "RELEASE_STATION: V2.1, V2.2, V3.0, and V4.0 Isolated and Verified"
        git push origin main
        ;;
    *)
        echo "Usage: ./manage.sh {deploy-v2.1|deploy-v4.0|audit-all|push}"
        ;;
esac
