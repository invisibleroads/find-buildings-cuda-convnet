CLASSIFIER_PATHS="
$HOME/Experiments/20140707-1149/myanmar0-1/classifiers/20140709-172831
$HOME/20140707-1149/myanmar0-2/classifiers/20140710-165500
$HOME/myanmar0-3/classifiers/20140711-031019
$HOME/myanmar0-4/classifiers/20140708-001953
"
IMAGE_NAMES="
myanmar0
myanmar1
myanmar2
myanmar3
myanmar4
"
export EXPERIMENT_NAME=`basename $(dirname $(dirname $(pwd)/$0))`
export EXAMPLE_DIMENSIONS=16x16
export OVERLAP_DIMENSIONS=8x8
export ARRAY_SHAPE=32,32,4
export ACTUAL_RADIUS=8
export RANDOM_SEED=crosscompute
export BATCH_SIZE=5k
export TILE_DIMENSIONS=1000,1000
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
