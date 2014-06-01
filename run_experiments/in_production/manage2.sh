BASE_FOLDER=`pwd`
CLASSIFIERS="
mali
tanzania
ethiopia
"
for CLASSIFIER in $CLASSIFIERS; do
    cd $BASE_FOLDER/$CLASSIFIER
    bash run.sh
done
