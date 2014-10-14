export CLASSIFIER_NAME="uganda"
export TRAINING_IMAGE_NAMES="
uganda0
uganda1
"
export EXAMPLE_METRIC_DIMENSIONS=19x19
export OVERLAP_METRIC_DIMENSIONS=9.5x9.5
export ARRAY_SHAPE=32,32,3
export TEST_IMAGE_NAME=uganda0
export TEST_PIXEL_BOUNDS=8317,8300,18317,13300
export MINIMUM_METRIC_RADIUS=9.5
export RANDOM_SEED=crosscompute
export BATCH_SIZE=10k
export TIMESTAMP=`date +"%Y%m%d-%H%M%S"`
bash prepare_train.sh
bash train.sh
