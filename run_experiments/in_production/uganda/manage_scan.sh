IMAGE_NAMES="
uganda0
uganda1
"
for IMAGE_NAME in $IMAGE_NAMES; do
    bash scan.sh \
        ~/Experiments/example_dimensions/uganda/classifiers/0.06 \
        ~/Links/satellite-images/$IMAGE_NAME \
        ~/Links/building-locations/$IMAGE_NAME \
        12x12 6x6 20x20x3 13.2
done
