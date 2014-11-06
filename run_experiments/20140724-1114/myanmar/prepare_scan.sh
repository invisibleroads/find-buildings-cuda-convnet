source ~/Projects/count-buildings/run_experiments/log.sh
LOG_PATH=$TEMPORARY_FOLDER/`basename $0`-`date +"%Y%m%d-%H%M%S"`.log
PIXEL_BOUNDS_LIST=`\
    get_tiles_from_image \
        --target_folder $TEMPORARY_FOLDER/tiles \
        --image_path $NORMALIZED_IMAGE_PATH \
        --tile_metric_dimensions $TILE_METRIC_DIMENSIONS \
        --overlap_metric_dimensions $EXAMPLE_METRIC_DIMENSIONS \
        --list_pixel_bounds`
for PIXEL_BOUNDS in $PIXEL_BOUNDS_LIST; do
    log get_arrays_from_image \
        --target_folder $TEMPORARY_FOLDER/arrays-$PIXEL_BOUNDS \
        --image_path $NORMALIZED_IMAGE_PATH \
        --tile_metric_dimensions $EXAMPLE_METRIC_DIMENSIONS \
        --overlap_metric_dimensions $OVERLAP_METRIC_DIMENSIONS \
        --included_pixel_bounds $PIXEL_BOUNDS
    log get_batches_from_arrays \
        --target_folder $TEMPORARY_FOLDER/batches-$PIXEL_BOUNDS \
        --random_seed $RANDOM_SEED \
        --arrays_folder $TEMPORARY_FOLDER/arrays-$PIXEL_BOUNDS \
        --batch_size $BATCH_SIZE \
        --array_shape $ARRAY_SHAPE
done
