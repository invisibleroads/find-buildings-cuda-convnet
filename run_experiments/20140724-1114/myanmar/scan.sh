source ~/Projects/count-buildings/run_experiments/log.sh
LOG_PATH=$TEMPORARY_FOLDER/`basename $0`-`date +"%Y%m%d-%H%M%S"`.log
rm $TEMPORARY_FOLDER/probabilities-*.csv

PIXEL_BOUNDS_LIST=`\
    get_tiles_from_image \
        --target_folder $TEMPORARY_FOLDER/tiles \
        --image_path $IMAGE_PATH \
        --tile_metric_dimensions $TILE_METRIC_DIMENSIONS \
        --overlap_metric_dimensions $EXAMPLE_METRIC_DIMENSIONS \
        --list_pixel_bounds`
for PIXEL_BOUNDS in $PIXEL_BOUNDS_LIST; do
    MAX_BATCH_INDEX=`get_index_from_batches \
        --batches_folder $TEMPORARY_FOLDER/batches-$PIXEL_BOUNDS`
    log ccn-predict options.cfg \
        --write-preds $TEMPORARY_FOLDER/probabilities-$PIXEL_BOUNDS.csv \
        --data-path $TEMPORARY_FOLDER/batches-$PIXEL_BOUNDS \
        --train-range 0 \
        --test-range 0-$MAX_BATCH_INDEX \
        -f $CLASSIFIER_PATH
done

cat $TEMPORARY_FOLDER/probabilities-*.csv > \
    $TEMPORARY_FOLDER/probabilities.csv
sed -i '/0,1,pixel_center_x,pixel_center_y/d' \
    $TEMPORARY_FOLDER/probabilities.csv
sed -i '1 i 0,1,pixel_center_x,pixel_center_y' \
    $TEMPORARY_FOLDER/probabilities.csv
PROBABILITY_FOLDER=$TEMPORARY_FOLDER/${CLASSIFIER_NAME}-probabilities
mkdir -p $PROBABILITY_FOLDER
cp $TEMPORARY_FOLDER/probabilities.csv $PROBABILITY_FOLDER/probabilities.csv
COUNTS_FOLDER=$TEMPORARY_FOLDER/${CLASSIFIER_NAME}-counts
log get_counts_from_probabilities \
    --target_folder $COUNTS_FOLDER \
    --probabilities_folder $PROBABILITY_FOLDER \
    --image_path $IMAGE_PATH
log get_counts_from_probabilities \
    --target_folder $TARGET_FOLDER \
    --probabilities_folder $PROBABILITY_FOLDER \
    --image_path $IMAGE_PATH \
    --actual_metric_radius $ACTUAL_RADIUS
