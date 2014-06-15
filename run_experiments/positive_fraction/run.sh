CLASSIFIER_NAME=$1
shift
IMAGE_NAMES=$@

EXAMPLE_DIMENSIONS=12,12
OVERLAP_DIMENSIONS=6,6
RANDOM_SEED=crosscompute
BATCH_SIZE=1k
EXPERIMENT_NAME=`basename $(dirname $(pwd)/$0)`
OUTPUT_FOLDER=~/Experiments/$EXPERIMENT_NAME/$CLASSIFIER_NAME
mkdir -p $OUTPUT_FOLDER
source ../log.sh
rm $LOG_PATH

POSITIVE_FRACTIONS="
0.50
0.40
0.30
0.20
0.15
0.10
0.05
0.01
0.005
0.001
"
for POSITIVE_FRACTION in $POSITIVE_FRACTIONS; do

    DATASET_FOLDERS=""
    for IMAGE_NAME in $IMAGE_NAMES; do
        echo $IMAGE_NAME | tee -a $LOG_PATH
        # log get_examples_from_points \
            # --target_folder $OUTPUT_FOLDER/examples/$IMAGE_NAME \
            # --random_seed $RANDOM_SEED \
            # --image_path ~/Links/satellite-images/$IMAGE_NAME \
            # --points_path ~/Links/building-locations/$IMAGE_NAME \
            # --example_dimensions $EXAMPLE_DIMENSIONS

        log get_dataset_from_examples \
            --target_folder $OUTPUT_FOLDER/training_dataset_$POSITIVE_FRACTION/$IMAGE_NAME \
            --random_seed $RANDOM_SEED \
            --examples_folder $OUTPUT_FOLDER/examples/$IMAGE_NAME \
            --batch_size $BATCH_SIZE \
            --positive_fraction $POSITIVE_FRACTION
        # pushd $OUTPUT_FOLDER
        # tar czvf $IMAGE_NAME-examples.tar.gz examples/$IMAGE_NAME
        # rm -rf examples/$IMAGE_NAME
        # popd
        DATASET_FOLDERS="$DATASET_FOLDERS $OUTPUT_FOLDER/training_dataset_$POSITIVE_FRACTION/$IMAGE_NAME"
    done

    log get_batches_from_datasets \
        --target_folder $OUTPUT_FOLDER/training_batches_$POSITIVE_FRACTION \
        --dataset_folders $DATASET_FOLDERS \
        --batch_size $BATCH_SIZE \
        --array_shape 20,20,3
    for IMAGE_NAME in $IMAGE_NAMES; do
        pushd $OUTPUT_FOLDER
        tar czvf $IMAGE_NAME-dataset.tar.gz training_dataset_$POSITIVE_FRACTION/$IMAGE_NAME
        rm -rf training_dataset_$POSITIVE_FRACTION/$IMAGE_NAME
        popd
    done

done

for POSITIVE_FRACTION in $POSITIVE_FRACTIONS; do

    MAX_BATCH_INDEX=`get_index_from_batches \
        --batches_folder $OUTPUT_FOLDER/training_batches_$POSITIVE_FRACTION`
    MAX_BATCH_INDEX_MINUS_ONE=$(expr $MAX_BATCH_INDEX - 1)
    log ccn-train options.cfg \
        --save-path $OUTPUT_FOLDER/classifiers \
        --data-path $OUTPUT_FOLDER/training_batches_$POSITIVE_FRACTION \
        --train-range 0-$(($MAX_BATCH_INDEX_MINUS_ONE > 0 ? $MAX_BATCH_INDEX_MINUS_ONE : 0)) \
        --test-range $MAX_BATCH_INDEX

    CONVNET_PATH=`ls -d -t -1 $OUTPUT_FOLDER/classifiers/ConvNet__* | head -n 1`
    CLASSIFIER_PATH=$OUTPUT_FOLDER/classifiers/$CLASSIFIER_NAME_$POSITIVE_FRACTION
    rm -rf $CLASSIFIER_PATH
    mv $CONVNET_PATH $CLASSIFIER_PATH
    log ccn-predict options.cfg \
        --write-preds $OUTPUT_FOLDER/probabilities_$POSITIVE_FRACTION.csv \
        --data-path $OUTPUT_FOLDER/training_batches_$POSITIVE_FRACTION \
        --train-range 0 \
        --test-range $MAX_BATCH_INDEX \
        -f $CLASSIFIER_PATH

done
