cd $(dirname $(pwd)/$0)
bash make_dataset.sh
bash train_and_test.sh sklearn.logistic_regression
bash train_and_test.sh sklearn.support_vector_classification
