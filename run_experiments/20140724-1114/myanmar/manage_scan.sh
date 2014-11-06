cd ~/Projects/count-buildings/run_experiments/20140724-1114/myanmar/

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
export TILE_METRIC_DIMENSIONS=1000,1000




if [ ! -d $TEMPORARY_FOLDER/batches-* ]; then
    bash prepare_scan.sh
    rm -rf $TEMPORARY_FOLDER/arrays-*
fi

export CLASSIFIER_PATH
export CLASSIFIER_NAME=`basename $CLASSIFIER_PATH`
bash scan.sh
