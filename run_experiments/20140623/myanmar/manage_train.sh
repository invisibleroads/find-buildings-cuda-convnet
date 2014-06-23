export CLASSIFIER_NAME=myanmar
export TRAINING_IMAGE_NAMES="myanmar0"
export EXAMPLE_DIMENSIONS=10x10
export OVERLAP_DIMENSIONS=5x5
export ARRAY_SHAPE=20,20,4
export POSITIVE_FRACTIONS="0.01"
export TEST_IMAGE_NAME=myanmar0
export TEST_PIXEL_BOUNDS=13260,2320,14060,2920
export MINIMUM_RADIUS=5
export RANDOM_SEED=crosscompute
export BATCH_SIZE=10k
export TIMESTAMP=`date +"%Y%m%d-%H%M%S"`
bash prepare.sh
bash train.sh
