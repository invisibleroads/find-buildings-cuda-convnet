source `dirname $BASH_SOURCE`/initialize.sh

PIXEL_BOUNDS=13260,2320,14060,2920

get_tiles_from_image \
    --target_folder $OUTPUT_FOLDER/tiles \
    --image_path $IMAGE_PATH \
    --included_pixel_bounds $PIXEL_BOUNDS

# python get_examples_from_points.py \
    # --target_folder $OUTPUT_FOLDER/examples \
    # --image_path $IMAGE_PATH \
    # --points_path $POINTS_PATH \
    # --example_dimensions 10x10

# python get_dataset_from_examples.py \
    # --target_folder $OUTPUT_FOLDER/training_dataset \
    # --examples_folder $OUTPUT_FOLDER/examples \
    # --excluded_pixel_bounds $PIXEL_BOUNDS

# python get_arrays_from_image.py \
    # --target_folder $OUTPUT_FOLDER/test_arrays \
    # --image_path $IMAGE_PATH \
    # --tile_dimensions 10x10 \
    # --overlap_dimensions 5x5 \
    # --included_pixel_bounds $PIXEL_BOUNDS
