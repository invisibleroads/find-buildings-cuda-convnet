EXPERIMENT_NAME=`basename $(dirname $(dirname $(pwd)/$0))`
CLASSIFIER_NAME=20140623-141718
IMAGE_NAMES="
myanmar0
"
for IMAGE_NAME in $IMAGE_NAMES; do
    bash scan.sh \
        ~/Experiments/$EXPERIMENT_NAME/myanmar/classifiers/$CLASSIFIER_NAME \
        ~/Links/satellite-images/$IMAGE_NAME \
        ~/Links/building-locations/$IMAGE_NAME \
        10x10 5x5 20,20,4 10
done
