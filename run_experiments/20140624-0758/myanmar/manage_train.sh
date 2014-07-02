export CLASSIFIER_NAME=myanmar
export TRAINING_IMAGE_NAMES="myanmar0"
export EXAMPLE_DIMENSIONS=16x16
export OVERLAP_DIMENSIONS=8x8
export ARRAY_SHAPE=32,32,4
export POSITIVE_FRACTIONS="0.007 0.005"
export TEST_IMAGE_NAME=myanmar0
export TEST_PIXEL_BOUNDS=0,0,10000,5000
export MINIMUM_RADIUS=8
export RANDOM_SEED=crosscompute
export BATCH_SIZE=10k
export TIMESTAMP=`date +"%Y%m%d-%H%M%S"`
# bash prepare_train.sh
bash train.sh