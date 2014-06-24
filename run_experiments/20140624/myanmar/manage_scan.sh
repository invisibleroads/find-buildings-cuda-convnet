CLASSIFIER_NAMES="
myanmar-20140618-1609
myanmar-20140622-144958
myanmar-20140623-141718
"
CLASSIFIER_NAMES="
myanmar-20140622-212724
myanmar-20140623-064851
myanmar-20140623-1509
"
export EXPERIMENT_NAME=`basename $(dirname $(dirname $(pwd)/$0))`
export IMAGE_NAME=myanmar0
export IMAGE_PATH=~/Links/satellite-images/$IMAGE_NAME
export POINTS_PATH=~/Links/building-locations/$IMAGE_NAME
export EXAMPLE_DIMENSIONS=10x10
export OVERLAP_DIMENSIONS=5x5
export ARRAY_SHAPE=20,20,4
export ACTUAL_RADIUS=10
export RANDOM_SEED=crosscompute
export BATCH_SIZE=5k
export TILE_DIMENSIONS=1000,1000
# bash prepare_scan.sh
for CLASSIFIER_NAME in $CLASSIFIER_NAMES; do
    export CLASSIFIER_NAME
    export CLASSIFIER_PATH=~/Storage/building-classifiers/$CLASSIFIER_NAME
    bash scan.sh
done
