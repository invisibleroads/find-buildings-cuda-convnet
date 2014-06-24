export CLASSIFIER_NAME=myanmar
export TRAINING_IMAGE_NAMES="myanmar0"
export EXAMPLE_DIMENSIONS=10x10
export OVERLAP_DIMENSIONS=5x5
export ARRAY_SHAPE=20,20,4
export POSITIVE_FRACTIONS="0.01"
export MAXIMUM_DATASET_SIZE=500k
export TEST_IMAGE_NAME=myanmar0
export TEST_PIXEL_BOUNDS=0,0,10000,5000
export MINIMUM_RADIUS=5
export RANDOM_SEED=crosscompute
export BATCH_SIZE=10k
export TIMESTAMP=`date +"%Y%m%d-%H%M%S"`
bash prepare_train.sh
bash train.sh