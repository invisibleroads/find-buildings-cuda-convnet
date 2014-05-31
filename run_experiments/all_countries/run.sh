OUTPUT_FOLDER=~/Experiments/primary/`basename $(dirname $(pwd)/$0)`
PIXEL_BOUNDS=13260,2320,14060,2920
EXAMPLE_DIMENSIONS=10x10
OVERLAP_DIMENSIONS=5x5
BATCH_SIZE=10k
RANDOM_SEED=myanmar

COUNTRY_IMAGES="
ethiopia0
mali0
myanmar0
senegal0
tanzania0
uganda0
uganda1
"
for COUNTRY_IMAGE in $COUNTRY_IMAGES; do
echo $COUNTRY_IMAGE
IMAGE_PATH=~/Links/satellite-images/$COUNTRY_IMAGE
POINTS_PATH=~/Links/building-locations/$COUNTRY_IMAGE
get_examples_from_points \
    --target_folder $OUTPUT_FOLDER/examples/$COUNTRY_IMAGE \
    --random_seed $RANDOM_SEED \
    --image_path $IMAGE_PATH \
    --points_path $POINTS_PATH \
    --example_dimensions $EXAMPLE_DIMENSIONS \
    --maximum_positive_count 210k \
    --maximum_negative_count 210k
get_dataset_from_examples \
    --target_folder $OUTPUT_FOLDER/training_dataset/$COUNTRY_IMAGE \
    --random_seed $RANDOM_SEED \
    --examples_folder $OUTPUT_FOLDER/examples/$COUNTRY_IMAGE \
    --excluded_pixel_bounds $PIXEL_BOUNDS \
    --maximum_dataset_size 210k
done
get_batches_from_datasets \
    --target_folder $OUTPUT_FOLDER/training_batches \
    --dataset_folders \
        $OUTPUT_FOLDER/training_dataset/ethiopia0 \
        $OUTPUT_FOLDER/training_dataset/mali0 \
        $OUTPUT_FOLDER/training_dataset/myanmar0 \
        $OUTPUT_FOLDER/training_dataset/senegal0 \
        $OUTPUT_FOLDER/training_dataset/tanzania0 \
        $OUTPUT_FOLDER/training_dataset/uganda0 \
        $OUTPUT_FOLDER/training_dataset/uganda1 \
    --batch_size $BATCH_SIZE

get_batches_from_datasets \
    --target_folder $OUTPUT_FOLDER/validation_batches \
    --dataset_folders \
        $OUTPUT_FOLDER/training_dataset/myanmar0 \
    --batch_size $BATCH_SIZE \
    --array_shape 17,17,3

COUNTRY_IMAGE=myanmar0
IMAGE_PATH=~/Links/satellite-images/$COUNTRY_IMAGE
get_arrays_from_image \
    --target_folder $OUTPUT_FOLDER/test_arrays \
    --image_path $IMAGE_PATH \
    --overlap_dimensions $OVERLAP_DIMENSIONS \
    --tile_dimensions $EXAMPLE_DIMENSIONS \
    --included_pixel_bounds $PIXEL_BOUNDS
get_batches_from_arrays \
    --target_folder $OUTPUT_FOLDER/test_batches \
    --arrays_folder $OUTPUT_FOLDER/test_arrays \
    --batch_size $BATCH_SIZE \
    --array_shape 17,17,3

# ccn-train options.cfg
# ccn-predict options.cfg -f $OUTPUT_FOLDER/ConvNet__*
