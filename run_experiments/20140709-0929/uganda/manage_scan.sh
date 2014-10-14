CLASSIFIER_PATHS="
$HOME/Experiments/20140709-0929/uganda0-1/classifiers/20140715-061930
"
IMAGE_NAMES="
uganda0
uganda1
"
export EXPERIMENT_NAME=`basename $(dirname $(dirname $(pwd)/$0))`
export EXAMPLE_METRIC_DIMENSIONS=19x19
export OVERLAP_METRIC_DIMENSIONS=9.5x9.5
export ARRAY_SHAPE=32,32,3
export ACTUAL_RADIUS=9.5
export RANDOM_SEED=crosscompute
export BATCH_SIZE=5k
export TILE_METRIC_DIMENSIONS=1000,1000
for IMAGE_NAME in $IMAGE_NAMES; do
    export IMAGE_NAME
    export IMAGE_PATH=~/Links/satellite-images/$IMAGE_NAME
    export POINTS_PATH=~/Links/building-locations/$IMAGE_NAME
    if [ ! -d ~/Downloads/$IMAGE_NAME/batches-0,0,2000,2000 ]; then
        bash prepare_scan.sh
        rm -rf ~/Downloads/$IMAGE_NAME/arrays-*
    fi
    for CLASSIFIER_PATH in $CLASSIFIER_PATHS; do
        export CLASSIFIER_PATH
        export CLASSIFIER_NAME=`basename $CLASSIFIER_PATH`
        bash scan.sh
    done
done
