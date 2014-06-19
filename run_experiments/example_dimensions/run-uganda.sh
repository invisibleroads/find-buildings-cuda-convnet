CLASSIFIER_NAME=$1
TRAINING_IMAGE_NAMES=$2
EXAMPLE_DIMENSIONS=$3
OVERLAP_DIMENSIONS=$4
TEST_IMAGE_NAME=$5
TEST_PIXEL_BOUNDS=$6
ACTUAL_RADIUS=$7

RANDOM_SEED=crosscompute
BATCH_SIZE=1k
EXPERIMENT_NAME=`basename $(dirname $(pwd)/$0)`
OUTPUT_FOLDER=~/Experiments/$EXPERIMENT_NAME/$CLASSIFIER_NAME
mkdir -p $OUTPUT_FOLDER
source ../log.sh
LOG_PATH=$OUTPUT_FOLDER/`basename $0`-`date +"%Y%m%d-%H%M%S"`.log

MAX_TEST_BATCH_INDEX=`get_index_from_batches \
    --batches_folder $OUTPUT_FOLDER/test_batches`
MAX_TEST_BATCH_INDEX_MINUS_ONE=$(expr $MAX_TEST_BATCH_INDEX - 1)

POSITIVE_FRACTIONS="
0.11
0.10
0.09
0.08
0.07
0.06
0.05
0.04
0.03
0.02
0.01
"
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
    CLASSIFIER_PATH=$OUTPUT_FOLDER/classifiers/$CLASSIFIER_NAME_$POSITIVE_FRACTION
    mv $CLASSIFIER_PATH /tmp
    mv $CONVNET_PATH $CLASSIFIER_PATH
    log ccn-predict options.cfg \
        --write-preds $OUTPUT_FOLDER/probabilities_$POSITIVE_FRACTION.csv \
        --data-path $OUTPUT_FOLDER/test_batches \
        --train-range 0 \
        --test-range 0-$MAX_TEST_BATCH_INDEX \
        -f $CLASSIFIER_PATH
    mkdir $OUTPUT_FOLDER/probabilities_$POSITIVE_FRACTION
    mv $OUTPUT_FOLDER/probabilities_$POSITIVE_FRACTION.csv $OUTPUT_FOLDER/probabilities_$POSITIVE_FRACTION/probabilities.csv
    log get_counts_from_probabilities \
        --target_folder $OUTPUT_FOLDER/counts_$POSITIVE_FRACTION \
        --probabilities_folder $OUTPUT_FOLDER/probabilities_$POSITIVE_FRACTION \
        --image_path ~/Links/satellite-images/myanmar0 \
        --points_path ~/Links/building-locations/myanmar0 \
        --actual_radius $ACTUAL_RADIUS

done
