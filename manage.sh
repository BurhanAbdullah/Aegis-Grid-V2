#!/bin/bash
export PYTHONPATH=$(pwd)

case "$1" in
    v2.1)
        echo "Running Aegis-Grid V2.1 Stable..."
        python3 -m releases.v2.1_stable.core.audit
        ;;
    v2.2)
        echo "Running Aegis-Grid V2.2 Cognitive..."
        python3 -m releases.v2.2_cognitive.core.audit
        ;;
    v3.0)
        echo "Running Aegis-Grid V3.0 Morphic..."
        python3 -m releases.v3.0_morphic.core.audit
        ;;
    v4.0)
        echo "Running Aegis-Grid V4.0 Hive-Cell..."
        python3 -m releases.v4.0_hive_cell.core.audit
        ;;
    *)
        echo "Usage: ./manage.sh {v2.1|v2.2|v3.0|v4.0}"
        ;;
esac
