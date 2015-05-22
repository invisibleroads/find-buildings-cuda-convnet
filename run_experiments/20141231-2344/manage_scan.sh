cd ~/Projects/count-buildings/run_experiments/20141231-2344

export TARGET_FOLDER=$1
export CLASSIFIER_PATH=$2
export IMAGE_PATH=$3
export TEMPORARY_FOLDER=`mktemp -d`

export EXAMPLE_METRIC_DIMENSIONS=16x16
export OVERLAP_METRIC_DIMENSIONS=8x8
export ARRAY_SHAPE=32,32,4
export ACTUAL_RADIUS=8
export RANDOM_SEED=crosscompute
export BATCH_SIZE=5k
export INTERVAL_LENGTH=100000

normalize_image \
    --target_folder $TEMPORARY_FOLDER/normalize_image \
    --image_path $IMAGE_PATH \
    --target_dtype uint8 \
    --target_meters_per_pixel_dimensions 0.5x0.5
export NORMALIZED_IMAGE_PATH=$TEMPORARY_FOLDER/normalize_image/image.tif

if [ ! -d $TEMPORARY_FOLDER/batches-* ]; then
    bash prepare_scan.sh
    rm -rf $TEMPORARY_FOLDER/arrays-*
fi
export CLASSIFIER_PATH
export CLASSIFIER_NAME=`basename $CLASSIFIER_PATH`
bash scan.sh
rm -rf $TEMPORARY_FOLDER
