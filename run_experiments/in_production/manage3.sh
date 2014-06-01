BASE_FOLDER=`pwd`
CLASSIFIERS="
generic
"
for CLASSIFIER in $CLASSIFIERS; do
    cd $BASE_FOLDER/$CLASSIFIER
    bash run.sh
done
