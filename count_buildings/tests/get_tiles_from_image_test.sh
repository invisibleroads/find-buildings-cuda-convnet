OUTPUT_FOLDER=~/Experiments/`basename -s .sh $0`
IMAGE_PATH=~/Links/satellite-images/test-geotiff
TILE_DIMENSIONS=400x300
OVERLAP_DIMENSIONS=10x10
TILE_INDICES=446
PIXEL_BOUNDS=13260,2320,14060,2920

get_tiles_from_image \
    --target_folder $OUTPUT_FOLDER/tile_indices \
    --image_path $IMAGE_PATH \
    --overlap_dimensions $OVERLAP_DIMENSIONS \
    --tile_dimensions $TILE_DIMENSIONS \
    --tile_indices $TILE_INDICES

get_tiles_from_image \
    --target_folder $OUTPUT_FOLDER/tile_dimensions \
    --image_path $IMAGE_PATH \
    --included_pixel_bounds $PIXEL_BOUNDS \
    --overlap_dimensions $OVERLAP_DIMENSIONS \
    --tile_dimensions $TILE_DIMENSIONS

get_tiles_from_image \
    --target_folder $OUTPUT_FOLDER/included_pixel_bounds \
    --image_path $IMAGE_PATH \
    --included_pixel_bounds $PIXEL_BOUNDS

get_tiles_from_image \
    --target_folder $OUTPUT_FOLDER/image_path \
    --image_path $IMAGE_PATH
