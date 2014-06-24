export CLASSIFIER_NAME=generic
export TRAINING_IMAGE_NAMES="ethiopia0 mali0 myanmar0 senegal0 tanzania0 uganda0 uganda1"
export EXAMPLE_DIMENSIONS=12x12
export OVERLAP_DIMENSIONS=6x6
export ARRAY_SHAPE=20,20,3
export POSITIVE_FRACTIONS="0.01"
export TEST_IMAGE_NAME=myanmar0
export TEST_PIXEL_BOUNDS=13260,2320,14060,2920
export MINIMUM_RADIUS=6
export RANDOM_SEED=crosscompute
export BATCH_SIZE=10k
export TIMESTAMP=`date +"%Y%m%d-%H%M%S"`
bash prepare_train.sh
bash train.sh
