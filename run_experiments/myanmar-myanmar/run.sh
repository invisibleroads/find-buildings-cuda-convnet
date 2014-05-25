cd $(dirname $(pwd)/$0)
bash make_dataset.sh
bash test_classifier.sh sklearn.logistic_regression
bash test_classifier.sh sklearn.support_vector_classification
