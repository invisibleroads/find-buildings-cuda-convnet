BASE_FOLDER=`pwd`
CLASSIFIERS="
myanmar
uganda
senegal
"
for CLASSIFIER in $CLASSIFIERS; do
    cd $BASE_FOLDER/$CLASSIFIER
    ccn-train options.cfg
done
