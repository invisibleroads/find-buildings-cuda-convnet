export OUTPUT_FOLDER=~/Experiments/in_production/`basename $(dirname $(pwd)/$0)`
EXAMPLE_DIMENSIONS=10x10
OVERLAP_DIMENSIONS=5x5
BATCH_SIZE=10k
RANDOM_SEED=crosscompute

COUNTRY_IMAGES="
myanmar0
"
for COUNTRY_IMAGE in $COUNTRY_IMAGES; do
echo $COUNTRY_IMAGE
IMAGE_PATH=~/Links/satellite-images/$COUNTRY_IMAGE
POINTS_PATH=~/Links/building-locations/$COUNTRY_IMAGE
get_examples_from_points \
    --target_folder $OUTPUT_FOLDER/examples/$COUNTRY_IMAGE \
    --random_seed $RANDOM_SEED \
    --image_path $IMAGE_PATH \
    --points_path $POINTS_PATH \
    --example_dimensions $EXAMPLE_DIMENSIONS
get_dataset_from_examples \
    --target_folder $OUTPUT_FOLDER/training_dataset/$COUNTRY_IMAGE \
    --random_seed $RANDOM_SEED \
    --examples_folder $OUTPUT_FOLDER/examples/$COUNTRY_IMAGE
done

DATASET_FOLDERS=""
for COUNTRY_IMAGE in $COUNTRY_IMAGES; do
    DATASET_FOLDERS="$DATASET_FOLDERS $OUTPUT_FOLDER/training_dataset/$COUNTRY_IMAGE"
done
get_batches_from_datasets \
    --target_folder $OUTPUT_FOLDER/training_batches \
    --dataset_folders $DATASET_FOLDERS \
    --batch_size $BATCH_SIZE

ccn-train options.cfg