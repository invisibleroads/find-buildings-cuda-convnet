OUTPUT_FOLDER=~/Experiments/`basename $0`
IMAGE_PATH=~/Links/satellite-images/test-image
TILE_DIMENSIONS=400x300
OVERLAP_DIMENSIONS=10x10
TILE_INDICES=446
INCLUDED_PIXEL_BOUNDS=13260,2320,14060,2920

get_tiles_from_image \
    --target_folder $OUTPUT_FOLDER/image_path \
    --image_path $IMAGE_PATH

get_tiles_from_image \
    --target_folder $OUTPUT_FOLDER/included_pixel_bounds \
    --image_path $IMAGE_PATH \
    --included_pixel_bounds $INCLUDED_PIXEL_BOUNDS

get_tiles_from_image \
    --target_folder $OUTPUT_FOLDER/tile_dimensions \
    --image_path $IMAGE_PATH \
    --tile_dimensions $TILE_DIMENSIONS \
    --overlap_dimensions $OVERLAP_DIMENSIONS \
    --included_pixel_bounds $INCLUDED_PIXEL_BOUNDS

get_tiles_from_image \
    --target_folder $OUTPUT_FOLDER/tile_indices \
    --image_path $IMAGE_PATH \
    --tile_dimensions $TILE_DIMENSIONS \
    --overlap_dimensions $OVERLAP_DIMENSIONS \
    --tile_indices $TILE_INDICES
