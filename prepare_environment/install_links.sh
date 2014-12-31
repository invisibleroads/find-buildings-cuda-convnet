IMAGE_FOLDER=~/Storage/business-datasets/ColumbiaUniversity
python prepare_links.py \
    --target_link_folder ~/Links \
    --source_image_folder $IMAGE_FOLDER \
    --source_table_path $IMAGE_FOLDER/features.csv \
    --maximum_positive_count 20 \
    --maximum_negative_count 20 \
    --example_metric_dimensions 16x16
