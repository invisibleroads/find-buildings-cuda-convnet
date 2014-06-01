export OUTPUT_FOLDER=~/Experiments/in_production/`basename $(dirname $(pwd)/$0)`
EXAMPLE_DIMENSIONS=12x12
OVERLAP_DIMENSIONS=5x5
BATCH_SIZE=10k
RANDOM_SEED=crosscompute

COUNTRY_IMAGES="
ethiopia0@
mali0@
myanmar0@
senegal0@
tanzania0@
uganda0@
uganda1@
"
DATASET_FOLDERS=""
for COUNTRY_IMAGE in $COUNTRY_IMAGES; do
    DATASET_FOLDERS="$DATASET_FOLDERS $OUTPUT_FOLDER/training_dataset_210k/$COUNTRY_IMAGE"
done
get_batches_from_datasets \
    --target_folder $OUTPUT_FOLDER/training_batches_210k \
    --dataset_folders $DATASET_FOLDERS \
    --batch_size $BATCH_SIZE

DATASET_FOLDERS=""
for COUNTRY_IMAGE in $COUNTRY_IMAGES; do
    DATASET_FOLDERS="$DATASET_FOLDERS $OUTPUT_FOLDER/training_dataset/$COUNTRY_IMAGE"
done
get_batches_from_datasets \
    --target_folder $OUTPUT_FOLDER/training_batches \
    --dataset_folders $DATASET_FOLDERS \
    --batch_size $BATCH_SIZE

ccn-train options.cfg
