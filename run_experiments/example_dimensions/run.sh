CLASSIFIER_NAME=$1
shift
IMAGE_NAMES=$@

EXAMPLE_DIMENSIONS=10,10
OVERLAP_DIMENSIONS=5,5
RANDOM_SEED=crosscompute
BATCH_SIZE=1k
EXPERIMENT_NAME=`basename $(dirname $(pwd)/$0)`
OUTPUT_FOLDER=~/Experiments/$EXPERIMENT_NAME/$CLASSIFIER_NAME
mkdir -p $OUTPUT_FOLDER
source ../log.sh
LOG_PATH=$OUTPUT_FOLDER/`basename $0`-`date +"%Y%m%d-%H%M%S"`.log

TEST_IMAGE=myanmar0
PIXEL_BOUNDS=13260,2320,14060,2920
log get_arrays_from_image \
    --target_folder $OUTPUT_FOLDER/test_arrays \
    --image_path ~/Links/satellite-images/$TEST_IMAGE \
    --points_path ~/Links/building-locations/$TEST_IMAGE \
    --overlap_dimensions $OVERLAP_DIMENSIONS \
    --tile_dimensions $EXAMPLE_DIMENSIONS \
    --included_pixel_bounds $PIXEL_BOUNDS
log get_batches_from_arrays \
    --target_folder $OUTPUT_FOLDER/test_batches \
    --arrays_folder $OUTPUT_FOLDER/test_arrays \
    --batch_size $BATCH_SIZE
pushd $OUTPUT_FOLDER
tar czvf ${TEST_IMAGE}_test_arrays.tar.gz test_arrays
rm -rf test_arrays
popd
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
"
for POSITIVE_FRACTION in $POSITIVE_FRACTIONS; do

    DATASET_FOLDERS=""
    for IMAGE_NAME in $IMAGE_NAMES; do
        echo $IMAGE_NAME | tee -a $LOG_PATH

        log get_examples_from_points \
            --target_folder $OUTPUT_FOLDER/examples/$IMAGE_NAME \
            --random_seed $RANDOM_SEED \
            --image_path ~/Links/satellite-images/$IMAGE_NAME \
            --points_path ~/Links/building-locations/$IMAGE_NAME \
            --example_dimensions $EXAMPLE_DIMENSIONS

        log get_dataset_from_examples \
            --target_folder $OUTPUT_FOLDER/training_dataset_$POSITIVE_FRACTION/$IMAGE_NAME \
            --random_seed $RANDOM_SEED \
            --examples_folder $OUTPUT_FOLDER/examples/$IMAGE_NAME \
            --excluded_pixel_bounds $PIXEL_BOUNDS \
            --batch_size $BATCH_SIZE \
            --positive_fraction $POSITIVE_FRACTION

        DATASET_FOLDERS="$DATASET_FOLDERS $OUTPUT_FOLDER/training_dataset_$POSITIVE_FRACTION/$IMAGE_NAME"
    done

    log get_batches_from_datasets \
        --target_folder $OUTPUT_FOLDER/training_batches_$POSITIVE_FRACTION \
        --dataset_folders $DATASET_FOLDERS \
        --batch_size $BATCH_SIZE
    for IMAGE_NAME in $IMAGE_NAMES; do
        pushd $OUTPUT_FOLDER
        tar czvf ${IMAGE_NAME}_training_dataset_${POSITIVE_FRACTION}.tar.gz training_dataset_$POSITIVE_FRACTION/$IMAGE_NAME
        rm -rf training_dataset_$POSITIVE_FRACTION/$IMAGE_NAME
        popd
    done

done

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
        --target_folder counts_$POSITIVE_FRACTION \
        --probabilities_folder probabilities_$POSITIVE_FRACTION \
        --image_path ~/Links/satellite-images/myanmar0 \
        --points_path ~/Links/building-locations/myanmar0 \
        --actual_radius 10

done
