OUTPUT_FOLDER=~/Experiments/`basename -s .sh $0`
IMAGE_PATH=~/Links/satellite-images/test-geotiff
POINTS_PATH=~/Links/building-locations/test-shapefile
EXAMPLE_DIMENSIONS=10x10

get_examples_from_points \
    --target_folder $OUTPUT_FOLDER/examples \
    --image_path $IMAGE_PATH \
    --points_path $POINTS_PATH \
    --example_dimensions $EXAMPLE_DIMENSIONS \
    --maximum_positive_count 25 \
    --maximum_negative_count 25 \
    --random_seed whee \
    --save_images
