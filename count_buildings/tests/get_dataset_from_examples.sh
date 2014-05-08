OUTPUT_FOLDER=~/Experiments/`basename -s .sh $0`
EXAMPLES_FOLDER=~/Experiments/get_examples_from_points/maximum_count
PIXEL_BOUNDS=13260,2320,14060,2920

get_dataset_from_examples \
    --target_folder $OUTPUT_FOLDER/excluded_pixel_bounds \
    --examples_folder $EXAMPLES_FOLDER \
    --maximum_dataset_size 1k \
    --preserve_ratio \
    --excluded_pixel_bounds $PIXEL_BOUNDS

get_dataset_from_examples \
    --target_folder $OUTPUT_FOLDER/preserve_ratio \
    --examples_folder $EXAMPLES_FOLDER \
    --maximum_dataset_size 1k \
    --preserve_ratio

get_dataset_from_examples \
    --target_folder $OUTPUT_FOLDER/maximum_dataset_size \
    --examples_folder $EXAMPLES_FOLDER \
    --maximum_dataset_size 5k
