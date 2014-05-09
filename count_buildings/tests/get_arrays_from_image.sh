OUTPUT_FOLDER=~/Experiments/`basename -s .sh $0`
IMAGE_PATH=~/Links/satellite-images/test-geotiff
PIXEL_BOUNDS=13260,2320,14060,2920
OVERLAP_DIMENSIONS=5x5
TILE_DIMENSIONS=10x10

get_arrays_from_image \
    --target_folder $OUTPUT_FOLDER/included_pixel_bounds \
    --image_path $IMAGE_PATH \
    --overlap_dimensions $OVERLAP_DIMENSIONS \
    --tile_dimensions $TILE_DIMENSIONS \
    --included_pixel_bounds $PIXEL_BOUNDS
