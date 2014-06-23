export CLASSIFIER_NAME=uganda
export TRAINING_IMAGE_NAMES="uganda0 uganda1"
export EXAMPLE_DIMENSIONS=12x12
export OVERLAP_DIMENSIONS=6x6
export ARRAY_SHAPE=20,20,3
export POSITIVE_FRACTIONS="0.07"
export TEST_IMAGE_NAME=uganda0
export TEST_PIXEL_BOUNDS=6100,6000,6900,6600
export MINIMUM_RADIUS=6
export RANDOM_SEED=crosscompute
export BATCH_SIZE=10k
export TIMESTAMP=`date +"%Y%m%d-%H%M%S"`
# bash prepare.sh
bash train.sh
