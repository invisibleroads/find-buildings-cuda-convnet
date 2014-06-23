EXPERIMENT_NAME=`basename $(dirname $(dirname $(pwd)/$0))`
CLASSIFIER_NAME=0.07
IMAGE_NAMES="
uganda0
uganda1
"
for IMAGE_NAME in $IMAGE_NAMES; do
    bash scan.sh \
        ~/Experiments/$EXPERIMENT_NAME/myanmar/classifiers/$CLASSIFIER_NAME \
        ~/Links/satellite-images/$IMAGE_NAME \
        ~/Links/building-locations/$IMAGE_NAME \
        12x12 6x6 20,20,3 13.2
done
