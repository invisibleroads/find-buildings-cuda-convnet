OUTPUT_FOLDER=~/Experiments/`basename -s .sh $0`
IMAGE_PATH=`realpath ~/Links/satellite-images/test-geotiff`
POINTS_PATH=`realpath ~/Links/building-locations/test-shapefile`
PIXEL_BOUNDS=13260,2320,14060,2920
OVERLAP_DIMENSIONS=6x6
TILE_DIMENSIONS=12x12

get_arrays_from_image \
    --target_folder $OUTPUT_FOLDER/included_pixel_bounds \
    --image_path $IMAGE_PATH \
    --points_path $POINTS_PATH \
    --overlap_dimensions $OVERLAP_DIMENSIONS \
    --tile_dimensions $TILE_DIMENSIONS \
    --included_pixel_bounds $PIXEL_BOUNDS
