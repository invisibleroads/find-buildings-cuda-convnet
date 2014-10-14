OUTPUT_FOLDER=~/Experiments/`basename -s .sh $0`
IMAGE_PATH=`realpath ~/Links/satellite-images/test-geotiff`
POINTS_PATH=`realpath ~/Links/building-locations/test-shapefile`
EXAMPLE_METRIC_DIMENSIONS=10x10

get_examples_from_points \
    --target_folder $OUTPUT_FOLDER/maximum_count \
    --image_path $IMAGE_PATH \
    --points_path $POINTS_PATH \
    --example_metric_dimensions $EXAMPLE_METRIC_DIMENSIONS \
    --maximum_positive_count 2000 \
    --maximum_negative_count 2000

get_examples_from_points \
    --target_folder $OUTPUT_FOLDER/save_images \
    --image_path $IMAGE_PATH \
    --points_path $POINTS_PATH \
    --example_metric_dimensions $EXAMPLE_METRIC_DIMENSIONS \
    --maximum_positive_count 100 \
    --maximum_negative_count 100 \
    --save_images
