CLASSIFIER_NAME=$1
shift
IMAGE_NAMES=$@

EXAMPLE_DIMENSIONS=12,12
OVERLAP_DIMENSIONS=6,6
RANDOM_SEED=crosscompute
BATCH_SIZE=10k
EXPERIMENT_NAME=`basename $(dirname $(pwd)/$0)`
OUTPUT_FOLDER=~/Experiments/$EXPERIMENT_NAME/$CLASSIFIER_NAME
LOG_PATH=$OUTPUT_FOLDER/run.log
mkdir -p $OUTPUT_FOLDER

DATASET_FOLDERS=""
for IMAGE_NAME in $IMAGE_NAMES; do
    date 2>&1 | tee -a $LOG_PATH
    get_examples_from_points \
        --target_folder $OUTPUT_FOLDER/examples/$IMAGE_NAME \
        --random_seed $RANDOM_SEED \
        --image_path ~/Links/satellite-images/$IMAGE_NAME \
        --points_path ~/Links/building-locations/$IMAGE_NAME \
        --example_dimensions $EXAMPLE_DIMENSIONS \
        --maximum_positive_count 1 \
        --maximum_negative_count 1 \
        2>&1 | tee -a $LOG_PATH
    date 2>&1 | tee -a $LOG_PATH
    get_dataset_from_examples \
        --target_folder $OUTPUT_FOLDER/training_dataset/$IMAGE_NAME \
        --random_seed $RANDOM_SEED \
        --examples_folder $OUTPUT_FOLDER/examples/$IMAGE_NAME \
        --batch_size $BATCH_SIZE \
        2>&1 | tee -a $LOG_PATH
    pushd $OUTPUT_FOLDER
    tar czvf $IMAGE_NAME-examples.tar.gz examples/$IMAGE_NAME
    rm -rf examples/$IMAGE_NAME
    popd
    DATASET_FOLDERS="$DATASET_FOLDERS $OUTPUT_FOLDER/training_dataset/$IMAGE_NAME"
done

date 2>&1 | tee -a $LOG_PATH
get_batches_from_datasets \
    --target_folder $OUTPUT_FOLDER/training_batches \
    --dataset_folders $DATASET_FOLDERS \
    --batch_size $BATCH_SIZE \
    --array_shape 20,20,3 \
    2>&1 | tee -a $LOG_PATH
for IMAGE_NAME in $IMAGE_NAMES; do
    pushd $OUTPUT_FOLDER
    tar czvf $IMAGE_NAME-dataset.tar.gz training_dataset/$IMAGE_NAME
    rm -rf training_dataset/$IMAGE_NAME
    popd
done

MAX_BATCH_INDEX=`get_index_from_batches \
    --batches_folder $OUTPUT_FOLDER/training_batches`
MAX_BATCH_INDEX_MINUS_ONE=$(expr $MAX_BATCH_INDEX - 1)
date 2>&1 | tee -a $LOG_PATH
ccn-train options.cfg \
    --save-path $OUTPUT_FOLDER/classifiers \
    --data-path $OUTPUT_FOLDER/training_batches \
    --train-range 0-$(($MAX_BATCH_INDEX_MINUS_ONE > 0 ? $MAX_BATCH_INDEX_MINUS_ONE : 0)) \
    --test-range $MAX_BATCH_INDEX \
    2>&1 | tee -a $LOG_PATH

CONVNET_PATH=`ls -d -t -1 $OUTPUT_FOLDER/classifiers/ConvNet__* | head -n 1`
CLASSIFIER_PATH=$OUTPUT_FOLDER/classifiers/$CLASSIFIER_NAME-n-1
rm -rf $CLASSIFIER_PATH
mv $CONVNET_PATH $CLASSIFIER_PATH
date 2>&1 | tee -a $LOG_PATH
ccn-predict options.cfg \
    --write-preds $OUTPUT_FOLDER/probabilities.csv \
    --data-path $OUTPUT_FOLDER/training_batches \
    --train-range 0 \
    --test-range $MAX_BATCH_INDEX \
    -f $CLASSIFIER_PATH \
    2>&1 | tee -a $LOG_PATH

ARRAY_SHAPE=`
    get_array_shape_from_batches \
        --batches_folder $OUTPUT_FOLDER/training_batches`
TILE_DIMENSIONS=1000,1000
pushd $OUTPUT_FOLDER
tar czvf $CLASSIFIER_NAME-batches.tar.gz training_batches
rm -rf training_batches
popd
for IMAGE_NAME in $IMAGE_NAMES; do
    PIXEL_BOUNDS_LIST=`\
        get_tiles_from_image \
            --target_folder ~/Downloads/$IMAGE_NAME/tiles \
            --image_path ~/Links/satellite-images/$IMAGE_NAME \
            --tile_dimensions $TILE_DIMENSIONS \
            --overlap_dimensions $EXAMPLE_DIMENSIONS \
            --list_pixel_bounds`
    for PIXEL_BOUNDS in $PIXEL_BOUNDS_LIST; do
        date 2>&1 | tee -a $LOG_PATH
        get_arrays_from_image \
            --target_folder ~/Downloads/$IMAGE_NAME/arrays-$PIXEL_BOUNDS \
            --image_path ~/Links/satellite-images/$IMAGE_NAME \
            --tile_dimensions $TILE_DIMENSIONS \
            --overlap_dimensions $EXAMPLE_DIMENSIONS \
            --included_pixel_bounds 500,500,550,550 \
            2>&1 | tee -a $LOG_PATH
        # --included_pixel_bounds $PIXEL_BOUNDS \
        date 2>&1 | tee -a $LOG_PATH
        get_batches_from_arrays \
            --target_folder ~/Downloads/$IMAGE_NAME/batches-$PIXEL_BOUNDS \
            --random_seed $RANDOM_SEED \
            --arrays_folder ~/Downloads/$IMAGE_NAME/arrays-$PIXEL_BOUNDS \
            --batch_size $BATCH_SIZE \
            --array_shape $ARRAY_SHAPE \
            2>&1 | tee -a $LOG_PATH
        pushd ~/Downloads
        tar czvf $IMAGE_NAME-arrays-$PIXEL_BOUNDS.tar.gz $IMAGE_NAME/arrays-$PIXEL_BOUNDS
        rm -rf $IMAGE_NAME/arrays-$PIXEL_BOUNDS
        popd

        MAX_BATCH_INDEX=`get_index_from_batches \
            --batches_folder ~/Downloads/$IMAGE_NAME/batches-$PIXEL_BOUNDS`
        date 2>&1 | tee -a $LOG_PATH
        ccn-predict options.cfg \
            --write-preds ~/Downloads/$IMAGE_NAME/probabilities.csv \
            --data-path ~/Downloads/$IMAGE_NAME/batches-$PIXEL_BOUNDS \
            --train-range 0 \
            --test-range 0-$MAX_BATCH_INDEX \
            -f $CLASSIFIER_PATH \
            2>&1 | tee -a $LOG_PATH
        cp ~/Downloads/$IMAGE_NAME/probabilities.csv ~/Downloads/$IMAGE_NAME/probabilities-$PIXEL_BOUNDS.csv
        pushd ~/Downloads
        tar czvf $IMAGE_NAME-batches-$PIXEL_BOUNDS.tar.gz $IMAGE_NAME/batches-$PIXEL_BOUNDS
        rm -rf $IMAGE_NAME/batches-$PIXEL_BOUNDS
        popd

        date 2>&1 | tee -a $LOG_PATH
        get_counts_from_probabilities \
            --target_folder ~/Downloads/$IMAGE_NAME/counts-$PIXEL_BOUNDS \
            --probabilities_folder ~/Downloads/$IMAGE_NAME \
            --image_path ~/Links/satellite-images/$IMAGE_NAME \
            --points_path ~/Links/building-locations/$IMAGE_NAME \
            2>&1 | tee -a $LOG_PATH
    done
done
date 2>&1 | tee -a $LOG_PATH
