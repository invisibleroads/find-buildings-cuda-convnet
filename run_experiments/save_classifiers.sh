TARGET_PATH=~/Experiments/in_production/classifiers.gz
SOURCE_FOLDERS="
$HOME/Experiments/in_production
$HOME/Projects/count-buildings
"

rm $TARGET_PATH
for SOURCE_FOLDER in $SOURCE_FOLDERS; do
    cd $SOURCE_FOLDER
    find . -name ConvNet__* -exec tar -rvf $TARGET_PATH {} \;
done
