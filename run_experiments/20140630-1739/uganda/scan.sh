source ~/Projects/count-buildings/run_experiments/log.sh
LOG_PATH=~/Downloads/$IMAGE_NAME/`basename $0`-`date +"%Y%m%d-%H%M%S"`.log
rm ~/Downloads/$IMAGE_NAME/probabilities-*.csv

PIXEL_BOUNDS_LIST=`\
    get_tiles_from_image \
        --target_folder ~/Downloads/$IMAGE_NAME/tiles \
        --image_path $IMAGE_PATH \
        --tile_metric_dimensions $TILE_METRIC_DIMENSIONS \
        --overlap_metric_dimensions $EXAMPLE_METRIC_DIMENSIONS \
        --list_pixel_bounds`
for PIXEL_BOUNDS in $PIXEL_BOUNDS_LIST; do
    MAX_BATCH_INDEX=`get_index_from_batches \
        --batches_folder ~/Downloads/$IMAGE_NAME/batches-$PIXEL_BOUNDS`
    log ccn-predict options.cfg \
        --write-preds ~/Downloads/$IMAGE_NAME/probabilities-$PIXEL_BOUNDS.csv \
        --data-path ~/Downloads/$IMAGE_NAME/batches-$PIXEL_BOUNDS \
        --train-range 0 \
        --test-range 0-$MAX_BATCH_INDEX \
        -f $CLASSIFIER_PATH
done

cat ~/Downloads/$IMAGE_NAME/probabilities-*.csv > \
    ~/Downloads/$IMAGE_NAME/probabilities.csv
sed -i '/0,1,pixel_center_x,pixel_center_y/d' \
    ~/Downloads/$IMAGE_NAME/probabilities.csv
sed -i '1 i 0,1,pixel_center_x,pixel_center_y' \
    ~/Downloads/$IMAGE_NAME/probabilities.csv
PROBABILITY_FOLDER=~/Downloads/$IMAGE_NAME/${IMAGE_NAME}-${CLASSIFIER_NAME}-probabilities
mkdir -p $PROBABILITY_FOLDER
cp ~/Downloads/$IMAGE_NAME/probabilities.csv $PROBABILITY_FOLDER/probabilities.csv
COUNTS_FOLDER=~/Downloads/$IMAGE_NAME/${IMAGE_NAME}-${CLASSIFIER_NAME}-counts
log get_counts_from_probabilities \
    --target_folder $COUNTS_FOLDER \
    --probabilities_folder $PROBABILITY_FOLDER \
    --image_path ~/Links/satellite-images/$IMAGE_NAME
log get_counts_from_probabilities \
    --target_folder ${COUNTS_FOLDER}-search \
    --probabilities_folder $PROBABILITY_FOLDER \
    --image_path ~/Links/satellite-images/$IMAGE_NAME \
    --points_path ~/Links/building-locations/$IMAGE_NAME \
    --minimum_metric_radius $MINIMUM_METRIC_RADIUS
