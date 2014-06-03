IMAGE_PATH=${1:-~/Links/satellite-images/myanmar0}
OPTIONS_PATH=$2
CONVNET_PATH=$3
PROBABILITIES_PATH=$4
PROBABILITIES_FOLDER=/tmp/get_probabilities_from_image
PIXEL_BOUNDS_LIST=`get_tiles_from_image \
    --target_folder /tmp/get_tiles_from_image/_ \
    --image_path $IMAGE_PATH \
    --tile_dimensions 1000x1000 \
    --overlap_dimensions 1010x1010 \
    --list_pixel_bounds`
PIXEL_BOUNDS_LIST="
28840,12900,30840,14900
28840,12920,30840,14920
"
for PIXEL_BOUNDS in $PIXEL_BOUNDS_LIST; do
    get_arrays_from_image.py \
        --target_folder FOLDER
        --random_seed STRING
        --image_path $IMAGE_PATH \
        --tile_dimensions WIDTH,HEIGHT
        --overlap_dimensions WIDTH,HEIGHT
        --included_pixel_bounds MIN_X,MIN_Y,MAX_X,MAX_Y
    get_batches_from_arrays \
        --target_folder FOLDER
        --random_seed STRING
        --arrays_folder FOLDER
        --batch_size SIZE
        --array_shape HEIGHT,WIDTH,BAND_COUNT
    ccn-predict $OPTIONS_PATH -f $CONVNET_PATH
    mv $PROBABILITIES_PATH $PROBABILITIES_FOLDER/probabilities-$PIXEL_BOUNDS.csv
    rm -rf $ARRAYS_FOLDER $BATCHES_FOLDER
done
