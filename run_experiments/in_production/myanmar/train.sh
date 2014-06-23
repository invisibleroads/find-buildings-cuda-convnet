EXPERIMENT_NAME=`basename $(dirname $(dirname $(pwd)/$0))`
OUTPUT_FOLDER=~/Experiments/$EXPERIMENT_NAME/$CLASSIFIER_NAME
mkdir -p $OUTPUT_FOLDER
source ~/Projects/count-buildings/run_experiments/log.sh
LOG_PATH=$OUTPUT_FOLDER/`basename $0`-$TIMESTAMP.log

MAX_TEST_BATCH_INDEX=`get_index_from_batches \
    --batches_folder $OUTPUT_FOLDER/test_batches`
MAX_TEST_BATCH_INDEX_MINUS_ONE=$(expr $MAX_TEST_BATCH_INDEX - 1)

for POSITIVE_FRACTION in $POSITIVE_FRACTIONS; do
    MAX_TRAINING_BATCH_INDEX=`get_index_from_batches \
        --batches_folder $OUTPUT_FOLDER/training_batches_$POSITIVE_FRACTION`
    MAX_TRAINING_BATCH_INDEX_MINUS_ONE=$(expr $MAX_TRAINING_BATCH_INDEX - 1)
    log ccn-train options.cfg \
        --save-path $OUTPUT_FOLDER/classifiers \
        --data-path $OUTPUT_FOLDER/training_batches_$POSITIVE_FRACTION \
        --train-range 0-$(($MAX_TRAINING_BATCH_INDEX_MINUS_ONE > 0 ? $MAX_TRAINING_BATCH_INDEX_MINUS_ONE : 0)) \
        --test-range $MAX_TRAINING_BATCH_INDEX

    CONVNET_PATH=`ls -d -t -1 $OUTPUT_FOLDER/classifiers/ConvNet__* | head -n 1`
    CLASSIFIER_PATH=$OUTPUT_FOLDER/classifiers/${POSITIVE_FRACTION}_${TIMESTAMP}
    mv $CONVNET_PATH $CLASSIFIER_PATH
    log ccn-predict options.cfg \
        --write-preds $OUTPUT_FOLDER/probabilities_$POSITIVE_FRACTION.csv \
        --data-path $OUTPUT_FOLDER/test_batches \
        --train-range 0 \
        --test-range 0-$MAX_TEST_BATCH_INDEX \
        -f $CLASSIFIER_PATH
    mkdir -p $OUTPUT_FOLDER/probabilities_$POSITIVE_FRACTION
    mv $OUTPUT_FOLDER/probabilities_$POSITIVE_FRACTION.csv $OUTPUT_FOLDER/probabilities_$POSITIVE_FRACTION/probabilities.csv
    log get_counts_from_probabilities \
        --target_folder $OUTPUT_FOLDER/counts_$POSITIVE_FRACTION \
        --probabilities_folder $OUTPUT_FOLDER/probabilities_$POSITIVE_FRACTION \
        --image_path ~/Links/satellite-images/$TEST_IMAGE_NAME \
        --points_path ~/Links/building-locations/$TEST_IMAGE_NAME \
        --minimum_radius $MINIMUM_RADIUS
done
