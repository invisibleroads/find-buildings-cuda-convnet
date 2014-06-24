CLASSIFIER_NAMES="
generic-20140622-0945
generic-20140622-1154
generic-20140622-1630
generic-20140623-0755
"
export EXPERIMENT_NAME=`basename $(dirname $(dirname $(pwd)/$0))`
export IMAGE_NAME=myanmar0
export IMAGE_PATH=~/Links/satellite-images/$IMAGE_NAME
export POINTS_PATH=~/Links/building-locations/$IMAGE_NAME
export EXAMPLE_DIMENSIONS=12x12
export OVERLAP_DIMENSIONS=6x6
export ARRAY_SHAPE=20,20,3
export ACTUAL_RADIUS=13.2
export RANDOM_SEED=crosscompute
export BATCH_SIZE=5k
export TILE_DIMENSIONS=1000,1000
# bash prepare_scan.sh
for CLASSIFIER_NAME in $CLASSIFIER_NAMES; do
    export CLASSIFIER_NAME
    export CLASSIFIER_PATH=~/Storage/building-classifiers/$CLASSIFIER_NAME
    bash scan.sh
done
