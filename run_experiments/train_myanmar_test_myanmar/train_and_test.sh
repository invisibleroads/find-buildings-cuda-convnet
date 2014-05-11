OUTPUT_FOLDER=~/Experiments/`basename $(dirname $(pwd)/$0)`
MARKER_MODULE=$1

python get_marker_from_dataset.py \
    --target_folder $OUTPUT_FOLDER/$MARKER_MODULE/marker \
    --dataset_folder $OUTPUT_FOLDER/training_dataset \
    --marker_module $MARKER_MODULE

python get_predictions_from_arrays.py \
    --target_folder $OUTPUT_FOLDER/$MARKER_MODULE/predictions \
    --marker_folder $OUTPUT_FOLDER/$MARKER_MODULE/marker \
    --arrays_folder $OUTPUT_FOLDER/test_arrays
