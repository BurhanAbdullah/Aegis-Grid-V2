#!/bin/bash
export PYTHONPATH=$PYTHONPATH:.

case "$1" in
    v2-audit)
        python3 -m v2_model.tests.stress.full_audit
        ;;
    v3-evolve)
        ./v3_fabric/fabric.sh evolve
        ;;
    v4-consensus)
        ./v4_hive/gate/hive_gate.sh "SECURE_DATA" "KEY_1000L"
        ;;
    compare)
        cat research_docs/VERSION_COMPARISON.md
        ;;
    push)
        git add .
        git commit -m "RESEARCH_UPDATE: Integrated V2-V4 Comparison Matrix"
        git push origin main
        ;;
    *)
        echo "Usage: ./manage.sh {v2-audit|v3-evolve|v4-consensus|compare|push}"
        ;;
esac
