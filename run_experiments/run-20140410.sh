SCRIPT_FOLDER=~/Projects/count-buildings
OUTPUT_FOLDER=~/Experiments/count_buildings
IMAGE_PATH=~/Links/satellite-images/Myanmar/o12JAN12044704-S2AS-053388615010_01_P001.tif
POINT_PATH=~/Links/building-locations/Myanmar/o12JAN12044704-S2AS-053388615010_01_P001.shp
cd $SCRIPT_FOLDER

# python get_tiles_from_image.py \
    # --target_folder $OUTPUT_FOLDER/t400x300 \
    # --image_path $IMAGE_PATH \
    # --tile_dimensions 400x300 \
    # --overlap_dimensions 10x10

# python get_examples_from_points.py \
    # --target_folder $OUTPUT_FOLDER/e10x10-Images \
    # --image_path $IMAGE_PATH \
    # --point_path $POINT_PATH \
    # --example_dimensions 10x10 \
    # --positive_count 5 \
    # --negative_count 5 \
    # --save_images
    
# python get_examples_from_points.py \
    # --target_folder $OUTPUT_FOLDER/e10x10-20140410 \
    # --image_path $IMAGE_PATH \
    # --point_path $POINT_PATH \
    # --example_dimensions 10x10 \

# python get_datasets_from_examples.py \
    # --target_folder $OUTPUT_FOLDER/e10x10-20140410-d10k \
    # --example_path $OUTPUT_FOLDER/e10x10-20140410/e10x10.h5 \
    # --dataset_size 10k \
    # --preserve_ratio

# python get_datasets_from_examples.py \
    # --target_folder $OUTPUT_FOLDER/e10x10-20140410-Production-Training \
    # --example_path ~/Experiments/count_buildings/e10x10/e10x10.h5 \
    # --stay_outside_pixel_bounds 13600,2400,14400,3000

python get_tiles_from_image.py \
    --target_folder $OUTPUT_FOLDER/t10x10-20140410-Production-Test \
    --image_path $IMAGE_PATH \
    --tile_dimensions 10,10 \
    --overlap_dimensions 5,5 \
    --stay_inside_pixel_bounds 13600,2400,14400,3000 \
    --save_arrays

# python get_marker_from_datasets.py \
    # --target_folder $OUTPUT_FOLDER/e10x10-20140410-LinearRegression \
    # --dataset_path $OUTPUT_FOLDER/e10x10-20140410-d10k/e10x10-d10k-p.h5

# python get_labels_from_marker.py
    # --target_folder $OUTPUT_FOLDER/t10x10-20140410-LinearRegression-Labels \
    # --marker_folder $OUTPUT_FOLDER/e10x10-20140410-LinearRegression \
    # --array_path $OUTPUT_FOLDER/t10x10-20140410-Production-Test/t10x10-o5x5 \

# python get_counts_from_labels.py
    # --target_folder $OUTPUT_FOLDER/t10x10-20140410-LinearRegression-Counts \
    # --label_folder $OUTPUT_FOLDER/t10x10-20140410-LinearRegression-Labels \
