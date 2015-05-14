source ~/Projects/count-buildings/run_experiments/log.sh
LOG_PATH=$TEMPORARY_FOLDER/`basename $0`-`date +"%Y%m%d-%H%M%S"`.log
rm $TEMPORARY_FOLDER/probabilities-*.csv

TILE_COUNT=`\
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

    MAX_BATCH_INDEX=`get_index_from_batches \
        --batches_folder $TEMPORARY_FOLDER/batches-$TILE_INDICES`
    log ccn-predict options.cfg \
        --write-preds $TEMPORARY_FOLDER/probabilities-$TILE_INDICES.csv \
        --data-path $TEMPORARY_FOLDER/batches-$TILE_INDICES \
        --train-range 0 \
        --test-range 0-$MAX_BATCH_INDEX \
        -f $CLASSIFIER_PATH

    let TILE_START_INDEX=TILE_END_INDEX+1
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
# COUNTS_FOLDER=$TEMPORARY_FOLDER/${CLASSIFIER_NAME}-counts
# log get_counts_from_probabilities \
    # --target_folder $COUNTS_FOLDER \
    # --probabilities_folder $PROBABILITY_FOLDER \
    # --image_path $NORMALIZED_IMAGE_PATH
log get_counts_from_probabilities \
    --target_folder $TARGET_FOLDER \
    --probabilities_folder $PROBABILITY_FOLDER \
    --image_path $NORMALIZED_IMAGE_PATH \
    --actual_metric_radius $ACTUAL_RADIUS
PREVIEW_FOLDER=$TEMPORARY_FOLDER/previews
log get_preview_from_points \
    --target_folder $PREVIEW_FOLDER \
    --random_seed $RANDOM_SEED \
    --image_path $IMAGE_PATH \
    --points_path $TARGET_FOLDER/counts.shp \
    --tile_pixel_dimensions 500x500 \
    --random_iteration_count 25
mv $PREVIEW_FOLDER/*.jpg $TARGET_FOLDER/preview.jpg
