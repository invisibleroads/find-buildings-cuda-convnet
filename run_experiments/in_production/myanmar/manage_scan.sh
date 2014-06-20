IMAGE_NAMES="
myanmar0
"
for IMAGE_NAME in $IMAGE_NAMES; do
bash scan.sh \
    ~/Experiments/example_dimensions/myanmar/classifiers/0.01 \
    ~/Links/satellite-images/$IMAGE_NAME \
    ~/Links/building-locations/$IMAGE_NAME \
    10x10 5x5 20x20x4 15
done
