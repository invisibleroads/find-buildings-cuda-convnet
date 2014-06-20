CLASSIFIER_PATH=$1
IMAGE_PATH=$2
IMAGE_NAME=`basename $IMAGE_PATH`
POINTS_PATH=$3
EXAMPLE_DIMENSIONS=$4
OVERLAP_DIMENSIONS=$5
ARRAY_SHAPE=$6
ACTUAL_RADIUS=$7

RANDOM_SEED=crosscompute
BATCH_SIZE=5k
TILE_DIMENSIONS=1000,1000

source ~/Projects/count-buildings/run_experiments/log.sh
LOG_PATH=~/Downloads/$IMAGE_NAME/`basename $0`-`date +"%Y%m%d-%H%M%S"`.log

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
        --points_path $POINTS_PATH \
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
    # pushd ~/Downloads
    # rm -rf $IMAGE_NAME/arrays-$PIXEL_BOUNDS
    # rm -rf $IMAGE_NAME/batches-$PIXEL_BOUNDS
    # popd
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
    --image_path ~/Links/satellite-images/$IMAGE_NAME
log get_counts_from_probabilities \
    --target_folder ~/Downloads/$IMAGE_NAME/counts \
    --probabilities_folder ~/Downloads/$IMAGE_NAME \
    --image_path ~/Links/satellite-images/$IMAGE_NAME \
    --points_path ~/Links/building-locations/$IMAGE_NAME \
    --actual_radius $ACTUAL_RADIUS
