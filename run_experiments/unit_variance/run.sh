OUTPUT_FOLDER=~/Experiments/primary/`basename $(dirname $(pwd)/$0)`
IMAGE_PATH=~/Links/satellite-images/myanmar0
POINTS_PATH=~/Links/building-locations/myanmar0
PIXEL_BOUNDS=13260,2320,14060,2920
EXAMPLE_DIMENSIONS=10x10
OVERLAP_DIMENSIONS=5x5
RANDOM_SEED=myanmar
BATCH_SIZE=10k

# cp -r ~/Experiments/primary/the_control/*_batches $OUTPUT_FOLDER

# ccn-train options_raw.cfg
# ccn-train options_unit_variance.cfg
# ccn-predict options.cfg -f $OUTPUT_FOLDER/ConvNet__*
