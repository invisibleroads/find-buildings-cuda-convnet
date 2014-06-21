IMAGE_NAMES="
myanmar0
"
for IMAGE_NAME in $IMAGE_NAMES; do
bash scan.sh \
    ~/Experiments/in_production/myanmar/classifiers/0.010 \
    ~/Links/satellite-images/$IMAGE_NAME \
    ~/Links/building-locations/$IMAGE_NAME \
    12x12 6x6 20,20,3 13.2
done
