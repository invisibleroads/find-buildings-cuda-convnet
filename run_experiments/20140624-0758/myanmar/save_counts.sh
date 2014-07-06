CLASSIFIER_NAME=`basename $(dirname $(pwd)/$0)`
EXPERIMENT_NAME=`basename $(dirname $(dirname $(pwd)/$0))`
TARGET_PATH=counts-${CLASSIFIER_NAME}-${EXPERIMENT_NAME}.gz
cd $HOME/Downloads
rm $TARGET_PATH
find . -name *.log -exec tar -rvf $TARGET_PATH {} \;
find . -name *-counts* -exec tar -rvf $TARGET_PATH {} \;
find . -name *-probabilities* -exec tar -rvf $TARGET_PATH {} \;
tar tvf $TARGET_PATH
