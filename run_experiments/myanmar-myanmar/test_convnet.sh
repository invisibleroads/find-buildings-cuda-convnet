OUTPUT_FOLDER=~/Experiments/`basename $(dirname $(pwd)/$0)`
MARKER_MODULE=cudaconv2
BATCH_SIZE=10k

get_batches_from_dataset \
    --target_folder $OUTPUT_FOLDER/$MARKER_MODULE/training_batches \
    --dataset_folder $OUTPUT_FOLDER/training_dataset \
    --batch_size $BATCH_SIZE

# get_batches_from_arrays \
    # --target_folder $OUTPUT_FOLDER/$MARKER_MODULE/test_batches \
    # --arrays_folder $OUTPUT_FOLDER/test_arrays \
    # --batch_size $BATCH_SIZE

# ccn-train options.cfg
# ccn-predict options.cfg -f $OUTPUT_FOLDER/$MARKER_MODULE/ConvNet__*
