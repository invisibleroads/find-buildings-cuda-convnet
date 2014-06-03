COUNTRIES="
ethiopia
mali
myanmar
senegal
tanzania
uganda
"
for COUNTRY in $COUNTRIES; do
    echo $COUNTRY
    ccn-train options.cfg \
        --save-path $COUNTRY \
        --data-path ~/Experiments/in_production/$COUNTRY/training_batches_210k \
    ccn-predict options.cfg \
        --write-preds ~/Experiments/in_production/$COUNTRY/probabilities.csv \
        --data-path ~/Experiments/in_production/$COUNTRY/training_batches_210k
done

echo generic
ccn-train options.cfg \
    --save-path generic \
    --data-path ~/Experiments/in_production/generic/training_batches_210k \
    --train-range 0-144 \
    --test-range 145
ccn-predict options.cfg \
    --write-preds ~/Experiments/in_production/generic/probabilities.csv \
    --data-path ~/Experiments/in_production/generic/training_batches_210k \
    --train-range 0-144 \
    --test-range 146
