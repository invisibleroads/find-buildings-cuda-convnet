EXPERIMENTS="
fc10_0.1
fc10_0.2
fc10_0.3
output_0.1
output_0.2
output_0.3
"
for EXPERIMENT in $EXPERIMENTS; do
    pushd $EXPERIMENT
    bash manage_train.sh
    popd
done
