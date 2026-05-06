#!/bin/bash

FILE="results.csv"

TP=0
FP=0
TN=0
FN=0

while IFS=, read -r cycle attack nis jitter traffic consensus
do
    if [[ "$cycle" == "cycle" ]]; then
        continue
    fi

    if [[ "$attack" == "1" && "$consensus" == "1" ]]; then
        ((TP++))
    elif [[ "$attack" == "0" && "$consensus" == "1" ]]; then
        ((FP++))
    elif [[ "$attack" == "0" && "$consensus" == "0" ]]; then
        ((TN++))
    elif [[ "$attack" == "1" && "$consensus" == "0" ]]; then
        ((FN++))
    fi

done < "$FILE"

echo "True Positives: $TP"
echo "False Positives: $FP"
echo "True Negatives: $TN"
echo "False Negatives: $FN"

RECALL=$(echo "scale=4; $TP / ($TP + $FN)" | bc)
FPR=$(echo "scale=4; $FP / ($FP + $TN)" | bc)

echo "Recall = $RECALL"
echo "False Positive Rate = $FPR"
