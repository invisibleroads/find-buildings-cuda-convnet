EXPERIMENT_NAME=`basename $(dirname $(pwd)/$0)`
TARGET_PATH=classifiers_${EXPERIMENT_NAME}.tar.gz
rm $TARGET_PATH
cd $HOME/Experiments/${EXPERIMENT_NAME}
find . -name ConvNet__* -exec tar -rvf $TARGET_PATH {} \;
find . -name *.log -exec tar -rvf $TARGET_PATH {} \;
