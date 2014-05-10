OUTPUT_FOLDER=~/Experiments/`basename -s .sh $0`
ARRAYS_FOLDER=~/Experiments/get_arrays_from_image/included_pixel_bounds
MARKER_FOLDER=~/Experiments/get_marker_from_dataset/marker_module

get_predictions_from_arrays \
    --target_folder $OUTPUT_FOLDER/marker_folder \
    --arrays_folder $ARRAYS_FOLDER \
    --marker_folder $MARKER_FOLDER
