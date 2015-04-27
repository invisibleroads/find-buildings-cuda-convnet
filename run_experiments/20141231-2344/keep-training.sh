TARGET_FOLDER=~/Storage/bits
CONFIGURATION_FOLDER=~/Projects/count-buildings/run_experiments/20141231-2344

get_marker_from_batches \
    --target_folder $TARGET_FOLDER/markers/generic \
    --random_seed crosscompute \
    --batch_folder $TARGET_FOLDER/batches/training \
    --testing_fraction 0.2 \
    --data_provider cropped-zero-mean \
    --crop_border_pixel_length 4 \
    --layer_definition_path $CONFIGURATION_FOLDER/layer-definition.cfg \
    --layer_parameters_path $CONFIGURATION_FOLDER/layer-parameters.cfg \
    --patience_epoch_count 100 \
    --source_marker_folder ~/Storage/bits/markers/generic/ConvNet__2015-03-18_01.13.59
