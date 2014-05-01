source initialize.sh

python get_marker_from_datasets.py \
    --target_folder $OUTPUT_FOLDER/logistic_regression/marker \
    --dataset_folders \
        $OUTPUT_FOLDER/training_dataset \
    --marker_module sklearn.logistic_regression

# python get_predictions_from_arrays.py \
    # --target_folder $OUTPUT_FOLDER/logistic_regression/predictions \
    # --marker_folder $OUTPUT_FOLDER/logistic_regression/marker \
    # --arrays_folder $OUTPUT_FOLDER/test_arrays
