OUTPUT_FOLDER=~/Experiments/in_production

COUNTRY_IMAGES="
ethiopia0
mali0
senegal0
tanzania0
uganda0
uganda1
"
for COUNTRY_IMAGE in $COUNTRY_IMAGES; do
    get_arrays_from_image \
        --target_folder $OUTPUT_FOLDER/$COUNTRY_IMAGE/arrays \
        --image_path ~/Links/satellite-images/$COUNTRY_IMAGE \
        --tile_dimensions 12x12 \
        --overlap_dimensions 6x6 \
        --included_pixel_bounds 5000,5000,7500,7500
    get_batches_from_arrays \
        --target_folder $OUTPUT_FOLDER/$COUNTRY_IMAGE/batches \
        --random_seed crosscompute \
        --arrays_folder $OUTPUT_FOLDER/$COUNTRY_IMAGE/arrays \
        --batch_size 10k \
        --array_shape 20,20,3
done

COUNTRY_IMAGES="
myanmar0
"
for COUNTRY_IMAGE in $COUNTRY_IMAGES; do
    get_arrays_from_image \
        --target_folder $OUTPUT_FOLDER/$COUNTRY_IMAGE/arrays \
        --image_path ~/Links/satellite-images/$COUNTRY_IMAGE \
        --tile_dimensions 10x10 \
        --overlap_dimensions 5x5 \
        --included_pixel_bounds 5000,5000,7500,7500
    get_batches_from_arrays \
        --target_folder $OUTPUT_FOLDER/$COUNTRY_IMAGE/batches \
        --random_seed crosscompute \
        --arrays_folder $OUTPUT_FOLDER/$COUNTRY_IMAGE/arrays \
        --batch_size 10k \
        --array_shape 20,20,3
done
