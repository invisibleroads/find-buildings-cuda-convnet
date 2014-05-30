OUTPUT_FOLDER=~/Experiments/primary/`basename $(dirname $(pwd)/$0)`
IMAGE_PATH=~/Links/satellite-images/myanmar0
POINTS_PATH=~/Links/building-locations/myanmar0
PIXEL_BOUNDS=13260,2320,14060,2920
EXAMPLE_DIMENSIONS=10x10
OVERLAP_DIMENSIONS=5x5
RANDOM_SEED=myanmar
BATCH_SIZE=10k

# cp -r ~/Experiments/primary/the_control/*_batches $OUTPUT_FOLDER

# ccn-train layers0/options.cfg
# ccn-train layers0-d0.1/options.cfg
# ccn-train layers0-d0.2/options.cfg
# ccn-train layers0-d0.5/options.cfg
# ccn-train layers1/options.cfg
# ccn-train layers1-fc5/options.cfg
# ccn-train layers1-fc64/options.cfg
# ccn-train layers2/options.cfg
# ccn-train layers2-fc5/options.cfg
# ccn-train layers2-fc64/options.cfg
# ccn-predict options.cfg -f $OUTPUT_FOLDER/ConvNet__*
