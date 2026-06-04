#!/usr/bin/env bash

set -euo pipefail

# =====================================================
# AEGIS v4
# Minimal Stable Research Engine
# =====================================================

STATE_DIR="state"
TRUST_FILE="$STATE_DIR/trust_v4.db"

mkdir -p "$STATE_DIR"
mkdir -p attacks
mkdir -p metrics
mkdir -p history

VALIDATORS=("A" "B" "C" "D")

# =====================================================
# PARAMETERS
# =====================================================

ALPHA=80

MIN_TRUST=25
MAX_TRUST=200

SLASH=30
RECOVER=1

PREPARE_THRESHOLD=55
COMMIT_THRESHOLD=55

JOIN_THRESHOLD=50
STAY_THRESHOLD=52

# =====================================================
# INIT TRUST DATABASE
# =====================================================

if [ ! -f "$TRUST_FILE" ]; then

cat > "$TRUST_FILE" <<EOF
A|90|95|92|91
B|88|90|85|87
C|93|92|94|90
D|70|80|60|75
EOF

fi

# =====================================================
# LOAD TRUST
# =====================================================

declare -A CRYPTO
declare -A BEHAVIOR
declare -A LATENCY
declare -A SENSOR
declare -A EFFECTIVE
declare -A CONFIDENCE
declare -A PARTICIPATING

while IFS='|' read -r V C B L S; do

    CRYPTO[$V]=$C
    BEHAVIOR[$V]=$B
    LATENCY[$V]=$L
    SENSOR[$V]=$S

done < "$TRUST_FILE"

# =====================================================
# RANDOM NETWORK CONDITIONS
# =====================================================

for V in "${VALIDATORS[@]}"; do

    LATENCY[$V]=$(( ${LATENCY[$V]} + RANDOM % 10 - 5 ))

    if [ "${LATENCY[$V]}" -lt 0 ]; then
        LATENCY[$V]=0
    fi

    if [ "${LATENCY[$V]}" -gt 100 ]; then
        LATENCY[$V]=100
    fi

done

# =====================================================
# BYZANTINE EVENTS
# =====================================================

for V in "${VALIDATORS[@]}"; do

    if (( RANDOM % 4 == 0 )); then

        echo "[BYZANTINE EVENT] $V equivocation"

        BEHAVIOR[$V]=$(( ${BEHAVIOR[$V]} - SLASH ))

    fi

done

# =====================================================
# EFFECTIVE TRUST + CONFIDENCE
# =====================================================

TOTAL_WEIGHT=0

for V in "${VALIDATORS[@]}"; do

    EFFECTIVE[$V]=$(( (
        40 * ${CRYPTO[$V]} +
        30 * ${BEHAVIOR[$V]} +
        15 * ${LATENCY[$V]} +
        15 * ${SENSOR[$V]}
    ) / 100 ))

    if [ "${EFFECTIVE[$V]}" -lt 0 ]; then
        EFFECTIVE[$V]=0
    fi

    CONFIDENCE[$V]=$(( (
        ${CRYPTO[$V]} +
        ${BEHAVIOR[$V]} +
        ${LATENCY[$V]} +
        ${SENSOR[$V]}
    ) / 4 ))

    if [ "${CONFIDENCE[$V]}" -lt 0 ]; then
        CONFIDENCE[$V]=0
    fi

    if [ "${EFFECTIVE[$V]}" -ge "$MIN_TRUST" ]; then

        TOTAL_WEIGHT=$(( TOTAL_WEIGHT + ${EFFECTIVE[$V]} ))

    fi

done

# =====================================================
# SAFETY ESTIMATION
# =====================================================

HONEST_ESTIMATE=0

for V in "${VALIDATORS[@]}"; do

    if [ "${CONFIDENCE[$V]}" -ge 55 ]; then

        HONEST_ESTIMATE=$(( HONEST_ESTIMATE + ${EFFECTIVE[$V]} ))

    fi

done

if [ "$TOTAL_WEIGHT" -gt 0 ]; then

    SAFETY=$(( 100 * HONEST_ESTIMATE / TOTAL_WEIGHT ))

else

    SAFETY=0

fi

# =====================================================
# ADAPTIVE QUORUM
# =====================================================

QUORUM_PERCENT=$(( 50 + ((100 - SAFETY) / 5) ))

if [ "$QUORUM_PERCENT" -gt 66 ]; then
    QUORUM_PERCENT=66
fi

if [ "$QUORUM_PERCENT" -lt 50 ]; then
    QUORUM_PERCENT=50
fi

QUORUM=$(( QUORUM_PERCENT * TOTAL_WEIGHT / 100 ))

# =====================================================
# PRIMARY SELECTION
# =====================================================

PRIMARY=""
BEST=0

for V in "${VALIDATORS[@]}"; do

    if [ "${EFFECTIVE[$V]}" -gt "$BEST" ]; then

        BEST=${EFFECTIVE[$V]}
        PRIMARY=$V

    fi

done

# =====================================================
# OUTPUT
# =====================================================

echo "================================="
echo "AEGIS v4"
echo "================================="
echo "Total trust weight : $TOTAL_WEIGHT"
echo "Adaptive quorum    : $QUORUM"
echo
echo "Safety envelope : ${SAFETY}%"
echo
echo "Primary selected : $PRIMARY"
echo "Primary trust    : $BEST"
echo

# =====================================================
# PREPARE PHASE
# =====================================================

PREPARE_WEIGHT=0

echo "----- PREPARE PHASE -----"

for V in "${VALIDATORS[@]}"; do

    W=${EFFECTIVE[$V]}
    CONF=${CONFIDENCE[$V]}

    if [ "${PARTICIPATING[$V]:-0}" -eq 1 ]; then
        THRESHOLD=$STAY_THRESHOLD
    else
        THRESHOLD=$JOIN_THRESHOLD
    fi

    if [ "$CONF" -ge "$THRESHOLD" ]; then

        PARTICIPATING[$V]=1

        PREPARE_WEIGHT=$(( PREPARE_WEIGHT + W ))

        echo "$V PREPARE yes weight=$W confidence=$CONF"

        BEHAVIOR[$V]=$(( ${BEHAVIOR[$V]} + RECOVER ))

    else

        PARTICIPATING[$V]=0

        echo "$V PREPARE abstain confidence=$CONF"

    fi

done

echo
echo "Prepare weight = $PREPARE_WEIGHT"

if [ "$PREPARE_WEIGHT" -lt "$QUORUM" ]; then

    echo "[FAIL] prepare quorum"

    exit 1

fi

# =====================================================
# COMMIT PHASE
# =====================================================

COMMIT_WEIGHT=0

echo
echo "----- COMMIT PHASE -----"

for V in "${VALIDATORS[@]}"; do

    W=${EFFECTIVE[$V]}
    CONF=${CONFIDENCE[$V]}

    if [ "$CONF" -ge "$COMMIT_THRESHOLD" ]; then

        COMMIT_WEIGHT=$(( COMMIT_WEIGHT + W ))

        echo "$V COMMIT yes weight=$W"

    else

        echo "$V COMMIT abstain"

    fi

done

echo
echo "Commit weight = $COMMIT_WEIGHT"

if [ "$COMMIT_WEIGHT" -lt "$QUORUM" ]; then

    echo "[FAIL] commit quorum"

    exit 1

fi

echo
echo "[SUCCESS] consensus finalized"

# =====================================================
# TRUST UPDATE
# =====================================================

TMP=$(mktemp)

for V in "${VALIDATORS[@]}"; do

    OBSERVED=$(( (
        ${CRYPTO[$V]} +
        ${BEHAVIOR[$V]} +
        ${LATENCY[$V]} +
        ${SENSOR[$V]}
    ) / 4 ))

    NEW=$(( (
        ALPHA * ${EFFECTIVE[$V]} +
        (100 - ALPHA) * OBSERVED
    ) / 100 ))

    if [ "$NEW" -gt "$MAX_TRUST" ]; then
        NEW=$MAX_TRUST
    fi

    if [ "$NEW" -lt 0 ]; then
        NEW=0
    fi

    echo "$V|$NEW|$NEW|$NEW|$NEW" >> "$TMP"

done

mv "$TMP" "$TRUST_FILE"

echo
echo "================================="
echo "AEGIS v4 completed"
echo "================================="
