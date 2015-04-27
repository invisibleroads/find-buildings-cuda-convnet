#!/bin/bash 
source ~/Projects/count-buildings/run_experiments/log.sh
LOG_PATH=$TEMPORARY_FOLDER/`basename $0`-`date +"%Y%m%d-%H%M%S"`.log

TILE_COUNT=`
    get_tiles_from_image \
        --target_folder $TEMPORARY_FOLDER/tiles \
        --image_path $NORMALIZED_IMAGE_PATH \
        --tile_metric_dimensions $EXAMPLE_METRIC_DIMENSIONS \
        --overlap_metric_dimensions $OVERLAP_METRIC_DIMENSIONS \
        --count_tiles`
TILE_START_INDEX=0

while [ $TILE_START_INDEX -lt $TILE_COUNT ]; do
    let TILE_END_INDEX=TILE_START_INDEX+INTERVAL_LENGTH-1
    TILE_INDICES=$TILE_START_INDEX-$TILE_END_INDEX

    log get_arrays_from_image \
        --target_folder $TEMPORARY_FOLDER/arrays-$TILE_INDICES \
        --image_path $NORMALIZED_IMAGE_PATH \
        --tile_indices $TILE_INDICES \
        --tile_metric_dimensions $EXAMPLE_METRIC_DIMENSIONS \
        --overlap_metric_dimensions $OVERLAP_METRIC_DIMENSIONS
    log get_batches_from_arrays \
        --target_folder $TEMPORARY_FOLDER/batches-$TILE_INDICES \
        --random_seed $RANDOM_SEED \
        --arrays_folder $TEMPORARY_FOLDER/arrays-$TILE_INDICES \
        --batch_size $BATCH_SIZE \
        --array_shape $ARRAY_SHAPE

    let TILE_START_INDEX=TILE_END_INDEX+1
done
