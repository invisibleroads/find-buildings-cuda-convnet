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
cp ~/Downloads/$IMAGE_NAME/probabilities.csv \
    ~/Downloads/$IMAGE_NAME/${IMAGE_NAME}-${CLASSIFIER_NAME}-probabilities.csv
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
cp -r ~/Downloads/$IMAGE_NAME/counts \
    ~/Downloads/$IMAGE_NAME/${IMAGE_NAME}-${CLASSIFIER_NAME}-counts
