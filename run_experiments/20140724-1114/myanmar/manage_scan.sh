cd ~/Projects/count-buildings/run_experiments/20140724-1114/myanmar/

export TARGET_FOLDER=$1
CLASSIFIER_PATH=$2
IMAGE_PATH=$3

export EXAMPLE_METRIC_DIMENSIONS=16x16
export OVERLAP_METRIC_DIMENSIONS=8x8
export ARRAY_SHAPE=32,32,4
export ACTUAL_RADIUS=8
export RANDOM_SEED=crosscompute
export BATCH_SIZE=5k
export TILE_METRIC_DIMENSIONS=1000,1000

export IMAGE_PATH
export IMAGE_NAME=`basename $IMAGE_PATH`
if [ ! -d ~/Downloads/$IMAGE_NAME/batches-0,0,2000,2000 ]; then
    bash prepare_scan.sh
    rm -rf ~/Downloads/$IMAGE_NAME/arrays-*
fi

export CLASSIFIER_PATH
export CLASSIFIER_NAME=`basename $CLASSIFIER_PATH`
bash scan.sh
