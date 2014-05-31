COUNTRY_IMAGES="
ethiopia0
mali0
myanmar0
senegal0
tanzania0
uganda0
uganda1
"
IMAGE_FOLDER=~/Links/satellite-images
POINTS_FOLDER=~/Links/building-locations
EXAMPLE_COUNT=10
EXAMPLE_DIMENSIONS=$1
OUTPUT_FOLDER=/tmp/see_countries/$EXAMPLE_DIMENSIONS

if [ -z "$EXAMPLE_DIMENSIONS" ]; then
    echo 'Please specify example dimensions'
    exit 1
fi

for COUNTRY_IMAGE in $COUNTRY_IMAGES; do
    get_examples_from_points \
        --target_folder $OUTPUT_FOLDER/$COUNTRY_IMAGE \
        --image_path $IMAGE_FOLDER/$COUNTRY_IMAGE \
        --points_path $POINTS_FOLDER/$COUNTRY_IMAGE \
        --example_dimensions $EXAMPLE_DIMENSIONS \
        --maximum_positive_count $EXAMPLE_COUNT \
        --maximum_negative_count $EXAMPLE_COUNT \
        --save_images
done
