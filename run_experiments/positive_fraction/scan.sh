CLASSIFIER_NAME=$1
CLASSIFIER_PATH=$2
IMAGE_PATH=$3
IMAGE_NAME=`basename $IMAGE_PATH`

EXAMPLE_DIMENSIONS=12,12
OVERLAP_DIMENSIONS=6,6
EXPERIMENT_NAME=`basename $(dirname $(pwd)/$0)`
OUTPUT_FOLDER=~/Experiments/$EXPERIMENT_NAME/$CLASSIFIER_NAME

ARRAY_SHAPE=20,20,3
TILE_DIMENSIONS=1000,1000

PIXEL_BOUNDS_LIST=`\
    get_tiles_from_image \
        --target_folder ~/Downloads/$IMAGE_NAME/tiles \
        --image_path $IMAGE_PATH \
        --tile_dimensions $TILE_DIMENSIONS \
        --overlap_dimensions $EXAMPLE_DIMENSIONS \
        --list_pixel_bounds`
for PIXEL_BOUNDS in $PIXEL_BOUNDS_LIST; do
    log get_arrays_from_image \
        --target_folder ~/Downloads/$IMAGE_NAME/arrays-$PIXEL_BOUNDS \
        --image_path $IMAGE_PATH \
        --tile_dimensions $EXAMPLE_DIMENSIONS \
        --overlap_dimensions $OVERLAP_DIMENSIONS \
        --included_pixel_bounds $PIXEL_BOUNDS
    log get_batches_from_arrays \
        --target_folder ~/Downloads/$IMAGE_NAME/batches-$PIXEL_BOUNDS \
        --random_seed $RANDOM_SEED \
        --arrays_folder ~/Downloads/$IMAGE_NAME/arrays-$PIXEL_BOUNDS \
        --batch_size $BATCH_SIZE \
        --array_shape $ARRAY_SHAPE

    MAX_BATCH_INDEX=`get_index_from_batches \
        --batches_folder ~/Downloads/$IMAGE_NAME/batches-$PIXEL_BOUNDS`
    log ccn-predict options.cfg \
        --write-preds ~/Downloads/$IMAGE_NAME/probabilities-$PIXEL_BOUNDS.csv \
        --data-path ~/Downloads/$IMAGE_NAME/batches-$PIXEL_BOUNDS \
        --train-range 0 \
        --test-range 0-$MAX_BATCH_INDEX \
        -f $CLASSIFIER_PATH
    log get_counts_from_probabilities \
        --target_folder ~/Downloads/$IMAGE_NAME/counts-$PIXEL_BOUNDS \
        --probabilities_folder ~/Downloads/$IMAGE_NAME \
        --image_path ~/Links/satellite-images/$IMAGE_NAME \
        --points_path ~/Links/building-locations/$IMAGE_NAME
    pushd ~/Downloads
    rm -rf $IMAGE_NAME/arrays-$PIXEL_BOUNDS
    rm -rf $IMAGE_NAME/batches-$PIXEL_BOUNDS
    popd
done

cat ~/Downloads/$IMAGE_NAME/probabilities-*.csv > \
    ~/Downloads/$IMAGE_NAME/probabilities.csv
sed -i '/0,1,pixel_center_x,pixel_center_y/d' \
    ~/Downloads/$IMAGE_NAME/probabilities.csv
sed -i '1 i 0,1,pixel_center_x,pixel_center_y' \
    ~/Downloads/$IMAGE_NAME/probabilities.csv
log get_counts_from_probabilities \
    --target_folder ~/Downloads/$IMAGE_NAME/counts \
    --probabilities_folder ~/Downloads/$IMAGE_NAME \
    --image_path ~/Links/satellite-images/$IMAGE_NAME \
    --points_path ~/Links/building-locations/$IMAGE_NAME \
    --actual_radius 12
