OUTPUT_FOLDER=~/Experiments/in_production/`basename $(dirname $(pwd)/$0)`
BATCH_SIZE=10k

BASE_FOLDER=~/Experiments/in_production
BATCH_FOLDER_NAME=training_batches
DATASET_FOLDER_NAME=training_dataset
get_batches_from_datasets \
    --target_folder $OUTPUT_FOLDER/$BATCH_FOLDER_NAME \
    --dataset_folders \
        $BASE_FOLDER/ethiopia/$DATASET_FOLDER_NAME/ethiopia0 \
        $BASE_FOLDER/mali/$DATASET_FOLDER_NAME/mali0 \
        $BASE_FOLDER/myanmar/$DATASET_FOLDER_NAME/myanmar0 \
        $BASE_FOLDER/senegal/$DATASET_FOLDER_NAME/senegal0 \
        $BASE_FOLDER/tanzania/$DATASET_FOLDER_NAME/tanzania0 \
        $BASE_FOLDER/uganda/$DATASET_FOLDER_NAME/uganda0 \
        $BASE_FOLDER/uganda/$DATASET_FOLDER_NAME/uganda1 \
    --batch_size $BATCH_SIZE \
    --array_shape 20,20,3

# ccn-train options.cfg
