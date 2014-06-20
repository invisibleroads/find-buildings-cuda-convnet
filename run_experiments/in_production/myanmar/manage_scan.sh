IMAGE_NAMES="
myanmar0
"
for IMAGE_NAME in $IMAGE_NAMES; do
bash scan.sh \
    ~/Experiments/in_production/myanmar/classifiers/0.010 \
    ~/Links/satellite-images/$IMAGE_NAME \
    ~/Links/building-locations/$IMAGE_NAME \
    10x10 5x5 20,20,4 15
done
