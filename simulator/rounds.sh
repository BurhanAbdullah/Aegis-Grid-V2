#!/usr/bin/env bash

set -uo pipefail

ROUNDS="${1:-10}"

mkdir -p metrics
mkdir -p history
mkdir -p attacks

RESULTS_FILE="metrics/results.csv"

echo "round,total_weight,quorum,safety,prepare_weight,commit_weight,primary,status" \
> "$RESULTS_FILE"

for ((ROUND=1; ROUND<=ROUNDS; ROUND++)); do

    echo
    echo "======================================="
    echo "ROUND $ROUND"
    echo "======================================="

    OUTPUT=$(bash core/consensus_v4.sh 2>&1) || true

    echo "$OUTPUT"

    # =====================================
    # STATUS
    # =====================================

    if echo "$OUTPUT" | grep -q "\[SUCCESS\] consensus finalized"; then

        STATUS="success"

    else

        STATUS="fail"

    fi

    # =====================================
    # METRICS
    # =====================================

    TOTAL_WEIGHT=$(echo "$OUTPUT" \
        | grep "Total trust weight" \
        | awk '{print $5}' \
        | tail -1)

    QUORUM=$(echo "$OUTPUT" \
        | grep "Adaptive quorum" \
        | awk '{print $4}' \
        | tail -1)

    SAFETY=$(echo "$OUTPUT" \
        | grep "Safety envelope" \
        | awk '{print $4}' \
        | tr -d '%' \
        | tail -1)

    PREPARE_WEIGHT=$(echo "$OUTPUT" \
        | grep "Prepare weight" \
        | awk '{print $4}' \
        | tail -1)

    COMMIT_WEIGHT=$(echo "$OUTPUT" \
        | grep "Commit weight" \
        | awk '{print $4}' \
        | tail -1)

    PRIMARY=$(echo "$OUTPUT" \
        | grep "Primary selected" \
        | awk '{print $4}' \
        | tail -1)

    TOTAL_WEIGHT=${TOTAL_WEIGHT:-0}
    QUORUM=${QUORUM:-0}
    SAFETY=${SAFETY:-0}
    PREPARE_WEIGHT=${PREPARE_WEIGHT:-0}
    COMMIT_WEIGHT=${COMMIT_WEIGHT:-0}
    PRIMARY=${PRIMARY:-none}

    echo "$ROUND,$TOTAL_WEIGHT,$QUORUM,$SAFETY,$PREPARE_WEIGHT,$COMMIT_WEIGHT,$PRIMARY,$STATUS" \
    >> "$RESULTS_FILE"

done

echo
echo "======================================="
echo "SIMULATION COMPLETE"
echo "======================================="

echo
echo "Results saved:"
echo "  $RESULTS_FILE"
