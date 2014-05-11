OUTPUT_FOLDER=~/Experiments/`basename $(dirname $(pwd)/$0)`
IMAGE_PATH=~/Links/satellite-images/Myanmar/o12JAN12044704-S2AS-053388615010_01_P001.tif
POINTS_PATH=~/Links/building-locations/Myanmar/o12JAN12044704-S2AS-053388615010_01_P001.shp
PIXEL_BOUNDS=13260,2320,14060,2920
EXAMPLE_DIMENSIONS=10x10
OVERLAP_DIMENSIONS=5x5
RANDOM_SEED=myanmar

get_tiles_from_image \
    --target_folder $OUTPUT_FOLDER/tiles \
    --image_path $IMAGE_PATH \
    --included_pixel_bounds $PIXEL_BOUNDS

get_examples_from_points \
    --target_folder $OUTPUT_FOLDER/examples \
    --random_seed $RANDOM_SEED \
    --image_path $IMAGE_PATH \
    --points_path $POINTS_PATH \
    --example_dimensions $EXAMPLE_DIMENSIONS

get_dataset_from_examples \
    --target_folder $OUTPUT_FOLDER/training_dataset \
    --random_seed $RANDOM_SEED \
    --examples_folder $OUTPUT_FOLDER/examples \
    --excluded_pixel_bounds $PIXEL_BOUNDS

get_arrays_from_image \
    --target_folder $OUTPUT_FOLDER/test_arrays \
    --image_path $IMAGE_PATH \
    --overlap_dimensions $OVERLAP_DIMENSIONS \
    --tile_dimensions $EXAMPLE_DIMENSIONS \
    --included_pixel_bounds $PIXEL_BOUNDS
