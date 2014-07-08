export OUTPUT_NAME="myanmar0-4"
CLASSIFIER_NAMES="
20140706-154132
"
IMAGE_NAMES="
myanmar0
"
export EXPERIMENT_NAME=`basename $(dirname $(dirname $(pwd)/$0))`
export EXAMPLE_DIMENSIONS=16x16
export OVERLAP_DIMENSIONS=8x8
export ARRAY_SHAPE=32,32,4
export MINIMUM_RADIUS=8
export RANDOM_SEED=crosscompute
export BATCH_SIZE=5k
export TILE_DIMENSIONS=1000,1000
for IMAGE_NAME in $IMAGE_NAMES; do
    export IMAGE_NAME
    export IMAGE_PATH=~/Links/satellite-images/$IMAGE_NAME
    export POINTS_PATH=~/Links/building-locations/$IMAGE_NAME
    bash prepare_scan.sh
    for CLASSIFIER_NAME in $CLASSIFIER_NAMES; do
        export CLASSIFIER_NAME
        export CLASSIFIER_PATH=~/Experiments/$EXPERIMENT_NAME/myanmar0-4/classifiers/$CLASSIFIER_NAME
        bash scan.sh
    done
    rm -rf ~/Downloads/$IMAGE_NAME/arrays-*
    rm -rf ~/Downloads/$IMAGE_NAME/batches-*
done
