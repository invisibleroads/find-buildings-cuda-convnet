OUTPUT_FOLDER=~/Experiments/primary/`basename $(dirname $(pwd)/$0)`
IMAGE_PATH=~/Links/satellite-images/myanmar0
POINTS_PATH=~/Links/building-locations/myanmar0
PIXEL_BOUNDS=13260,2320,14060,2920
EXAMPLE_DIMENSIONS=10x10
OVERLAP_DIMENSIONS=5x5
RANDOM_SEED=myanmar
BATCH_SIZE=10k

get_examples_from_points \
    --target_folder $OUTPUT_FOLDER/examples \
    --random_seed $RANDOM_SEED \
    --image_path $IMAGE_PATH \
    --points_path $POINTS_PATH \
    --example_dimensions $EXAMPLE_DIMENSIONS \
    --maximum_positive_count 110k \
    --maximum_negative_count 110k

get_dataset_from_examples \
    --target_folder $OUTPUT_FOLDER/training_dataset \
    --random_seed $RANDOM_SEED \
    --examples_folder $OUTPUT_FOLDER/examples \
    --excluded_pixel_bounds $PIXEL_BOUNDS \
    --maximum_dataset_size 110k

get_arrays_from_image \
    --target_folder $OUTPUT_FOLDER/test_arrays \
    --image_path $IMAGE_PATH \
    --overlap_dimensions $OVERLAP_DIMENSIONS \
    --tile_dimensions $EXAMPLE_DIMENSIONS \
    --included_pixel_bounds $PIXEL_BOUNDS

get_batches_from_dataset \
    --target_folder $OUTPUT_FOLDER/training_batches \
    --dataset_folder $OUTPUT_FOLDER/training_dataset \
    --batch_size $BATCH_SIZE

get_batches_from_arrays \
    --target_folder $OUTPUT_FOLDER/test_batches \
    --arrays_folder $OUTPUT_FOLDER/test_arrays \
    --batch_size $BATCH_SIZE

# ccn-train options.cfg
# ccn-predict options.cfg -f $OUTPUT_FOLDER/ConvNet__*
