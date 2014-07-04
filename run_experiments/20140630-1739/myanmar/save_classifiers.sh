CLASSIFIER_NAME=`basename $(dirname $(pwd)/$0)`
EXPERIMENT_NAME=`basename $(dirname $(dirname $(pwd)/$0))`
TARGET_PATH=classifiers-${CLASSIFIER_NAME}-${EXPERIMENT_NAME}.gz
rm $TARGET_PATH
cd $HOME/Experiments/${EXPERIMENT_NAME}
find . -name classifiers -exec tar -rvf $TARGET_PATH {} \;
find . -name *.log -exec tar -rvf $TARGET_PATH {} \;
find . -name *-counts* -exec tar -rvf $TARGET_PATH {} \;
find . -name *-probabilities* -exec tar -rvf $TARGET_PATH {} \;
tar tvf $TARGET_PATH
