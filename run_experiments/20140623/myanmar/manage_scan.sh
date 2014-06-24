export EXPERIMENT_NAME=`basename $(dirname $(dirname $(pwd)/$0))`
export CLASSIFIER_NAME=20140623-141718
export IMAGE_NAME=myanmar0
export CLASSIFIER_PATH=~/Experiments/$EXPERIMENT_NAME/myanmar/classifiers/$CLASSIFIER_NAME
export IMAGE_PATH=~/Links/satellite-images/$IMAGE_NAME
export POINTS_PATH=~/Links/building-locations/$IMAGE_NAME
export EXAMPLE_DIMENSIONS=10x10
export OVERLAP_DIMENSIONS=5x5
export ARRAY_SHAPE=20,20,4
export ACTUAL_RADIUS=10
export RANDOM_SEED=crosscompute
export BATCH_SIZE=5k
export TILE_DIMENSIONS=1000,1000
bash prepare_scan.sh
bash scan.sh
