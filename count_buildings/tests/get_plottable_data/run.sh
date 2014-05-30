OUTPUT_FOLDER=~/Experiments/get_plottable_data

# get_tiles_from_image \
    # --image_path ~/Links/satellite-images/myanmar0 \
    # --included_pixel_bounds 19900,14000,20100,14250

# get_arrays_from_image \
    # --target_folder $OUTPUT_FOLDER/arrays \
    # --image_path ~/Links/satellite-images/myanmar0 \
    # --included_pixel_bounds 500,500,2500,1500 
# python plot_arrays.py

# python plot_cifar_10.py
# ccn-make-batches options.cfg; python plot_batches_noccn.py

# get_batches_from_arrays \
    # --target_folder $OUTPUT_FOLDER/get_batches_from_arrays \
    # --arrays_folder $OUTPUT_FOLDER/arrays \
    # --batch_size 1k
# python plot_batches_from_arrays.py

COUNTRY_IMAGES="
ethiopia0
mali0
myanmar0
senegal0
tanzania0
uganda0
uganda1
"
for COUNTRY_IMAGE in $COUNTRY_IMAGES; do
    echo $COUNTRY_IMAGE
    get_examples_from_points \
        --target_folder $OUTPUT_FOLDER/examples/$COUNTRY_IMAGE \
        --image_path ~/Links/satellite-images/$COUNTRY_IMAGE \
        --points_path ~/Links/building-locations/$COUNTRY_IMAGE \
        --example_dimensions 100x50 \
        --maximum_positive_count 1 \
        --maximum_negative_count 1
    python plot_example.py $OUTPUT_FOLDER/examples/$COUNTRY_IMAGE
    get_dataset_from_examples \
        --target_folder $OUTPUT_FOLDER/dataset/$COUNTRY_IMAGE \
        --examples_folder $OUTPUT_FOLDER/examples/$COUNTRY_IMAGE
    python plot_dataset.py $OUTPUT_FOLDER/dataset/$COUNTRY_IMAGE
done
get_batches_from_datasets \
    --target_folder $OUTPUT_FOLDER/get_batches_from_datasets \
    --dataset_folders \
        $OUTPUT_FOLDER/dataset/ethiopia0 \
        $OUTPUT_FOLDER/dataset/myanmar0 \
        $OUTPUT_FOLDER/mali0 \
        $OUTPUT_FOLDER/senegal0 \
        $OUTPUT_FOLDER/tanzania0 \
        $OUTPUT_FOLDER/uganda0 \
        $OUTPUT_FOLDER/uganda1 \
    --batch_size 1k
python plot_batches_from_datasets.py
