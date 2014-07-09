EXPERIMENT_NAME=`basename $(dirname $(dirname $(pwd)/$0))`
OUTPUT_FOLDER=~/Experiments/$EXPERIMENT_NAME/$OUTPUT_NAME
mkdir -p $OUTPUT_FOLDER
source ~/Projects/count-buildings/run_experiments/log.sh
LOG_PATH=$OUTPUT_FOLDER/`basename $0`-$TIMESTAMP.log

# log get_arrays_from_image \
    # --target_folder $OUTPUT_FOLDER/test_arrays \
    # --image_path ~/Links/satellite-images/$TEST_IMAGE_NAME \
    # --points_path ~/Links/building-locations/$TEST_IMAGE_NAME \
    # --overlap_dimensions $OVERLAP_DIMENSIONS \
    # --tile_dimensions $EXAMPLE_DIMENSIONS \
    # --included_pixel_bounds $TEST_PIXEL_BOUNDS
# log get_batches_from_arrays \
    # --target_folder $OUTPUT_FOLDER/test_batches \
    # --random_seed $RANDOM_SEED \
    # --arrays_folder $OUTPUT_FOLDER/test_arrays \
    # --batch_size $BATCH_SIZE \
    # --array_shape $ARRAY_SHAPE
pushd $OUTPUT_FOLDER
# tar czvf ${TEST_IMAGE_NAME}_test_arrays.tar.gz test_arrays
# rm -rf test_arrays
popd
MAX_TEST_BATCH_INDEX=`get_index_from_batches \
    --batches_folder $OUTPUT_FOLDER/test_batches`
MAX_TEST_BATCH_INDEX_MINUS_ONE=$(expr $MAX_TEST_BATCH_INDEX - 1)

for IMAGE_NAME in $TRAINING_IMAGE_NAMES; do
    echo $IMAGE_NAME | tee -a $LOG_PATH
    ROADS_PATH=~/Links/road-locations/$IMAGE_NAME
    if [ -f $ROADS_PATH ]; then
        GET_EXAMPLES_FROM_POINTS="--negative_points_paths $ROADS_PATH"
    else
        GET_EXAMPLES_FROM_POINTS=""
    fi
    # log get_examples_from_points \
        # --target_folder $OUTPUT_FOLDER/examples/$IMAGE_NAME \
        # --random_seed $RANDOM_SEED \
        # --image_path ~/Links/satellite-images/$IMAGE_NAME \
        # --example_dimensions $EXAMPLE_DIMENSIONS \
        # --positive_points_paths \
            # ~/Links/building-locations/$IMAGE_NAME \
        # $GET_EXAMPLES_FROM_POINTS
    pushd $OUTPUT_FOLDER
    # tar czvf ${IMAGE_NAME}_examples.tar.gz examples/$IMAGE_NAME
    popd
done

DATASET_FOLDERS=""
for IMAGE_NAME in $TRAINING_IMAGE_NAMES; do
    echo $IMAGE_NAME | tee -a $LOG_PATH
    # log get_dataset_from_examples \
        # --target_folder $OUTPUT_FOLDER/training_dataset/$IMAGE_NAME \
        # --random_seed $RANDOM_SEED \
        # --examples_folder $OUTPUT_FOLDER/examples/$IMAGE_NAME \
        # --batch_size $BATCH_SIZE
    DATASET_FOLDERS="$DATASET_FOLDERS $OUTPUT_FOLDER/training_dataset/$IMAGE_NAME"
done

log get_batches_from_datasets \
    --target_folder $OUTPUT_FOLDER/training_batches \
    --random_seed $RANDOM_SEED \
    --dataset_folders $DATASET_FOLDERS \
    --batch_size $BATCH_SIZE \
    --array_shape $ARRAY_SHAPE
for IMAGE_NAME in $TRAINING_IMAGE_NAMES; do
    pushd $OUTPUT_FOLDER
    tar czvf ${IMAGE_NAME}_training_dataset.tar.gz training_dataset/$IMAGE_NAME
    rm -rf training_dataset/$IMAGE_NAME
    popd
done
