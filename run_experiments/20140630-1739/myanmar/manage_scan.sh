OUTPUT_NAME="myanmar0-4"
CLASSIFIER_NAMES="
20140702-034531
"
export EXPERIMENT_NAME=`basename $(dirname $(dirname $(pwd)/$0))`
export IMAGE_NAME=myanmar0
export IMAGE_PATH=~/Links/satellite-images/$IMAGE_NAME
export POINTS_PATH=~/Links/building-locations/$IMAGE_NAME
export EXAMPLE_METRIC_DIMENSIONS=16x16
export OVERLAP_METRIC_DIMENSIONS=8x8
export ARRAY_SHAPE=32,32,4
export MINIMUM_METRIC_RADIUS=8
export RANDOM_SEED=crosscompute
export BATCH_SIZE=5k
export TILE_METRIC_DIMENSIONS=1000,1000
bash prepare_scan.sh
for CLASSIFIER_NAME in $CLASSIFIER_NAMES; do
    export CLASSIFIER_NAME
    export CLASSIFIER_PATH=~/Experiments/20140630-1739/$OUTPUT_NAME/classifiers/$CLASSIFIER_NAME
    bash scan.sh
done
