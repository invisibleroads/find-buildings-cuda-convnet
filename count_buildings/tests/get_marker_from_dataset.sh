OUTPUT_FOLDER=~/Experiments/`basename -s .sh $0`
DATASET_FOLDER=~/Experiments/get_dataset_from_examples/excluded_pixel_bounds
MARKER_MODULE=sklearn.logistic_regression

get_marker_from_dataset \
    --target_folder $OUTPUT_FOLDER/marker_module \
    --dataset_folder $DATASET_FOLDER \
    --marker_module $MARKER_MODULE

get_marker_from_dataset \
    --target_folder $OUTPUT_FOLDER/cross_validate \
    --dataset_folder $DATASET_FOLDER \
    --marker_module $MARKER_MODULE \
    --cross_validate
