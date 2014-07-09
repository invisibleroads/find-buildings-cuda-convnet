export EXAMPLE_DIMENSIONS=16x16
export OVERLAP_DIMENSIONS=8x8
export ARRAY_SHAPE=32,32,4
export TEST_IMAGE_NAME=myanmar0
export TEST_PIXEL_BOUNDS=0,0,10000,5000
export MINIMUM_RADIUS=8
export RANDOM_SEED=crosscompute
export BATCH_SIZE=10k

export OUTPUT_NAME="myanmar0-1"
export TRAINING_IMAGE_NAMES="myanmar0 myanmar1"
export TIMESTAMP=`date +"%Y%m%d-%H%M%S"`
bash prepare_train.sh
bash train.sh

export OUTPUT_NAME="myanmar0-2"
export TRAINING_IMAGE_NAMES="myanmar0 myanmar1 myanmar2"
export TIMESTAMP=`date +"%Y%m%d-%H%M%S"`
bash prepare_train.sh
bash train.sh

export OUTPUT_NAME="myanmar0-3"
export TRAINING_IMAGE_NAMES="myanmar0 myanmar1 myanmar2 myanmar3"
export TIMESTAMP=`date +"%Y%m%d-%H%M%S"`
bash prepare_train.sh
bash train.sh
