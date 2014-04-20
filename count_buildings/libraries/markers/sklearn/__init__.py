import numpy as np
import os
from sklearn.cross_validation import cross_val_score
from sklearn.externals import joblib

from .. import AbstractMarker
from ... import dataset
from ...preparations.flat import flatten


class ScikitLearnMarker(AbstractMarker):

    def calibrate(self, dataset_path):
        arrays, labels = load_prepared_arrays_and_labels(dataset_path)
        self.model = self.Model()
        self.model.fit(arrays, labels)

    def cross_validate(self, dataset_path):
        arrays, labels = load_prepared_arrays_and_labels(dataset_path)
        return {
            'f1': np.mean(cross_val_score(
                self.Model(), arrays, labels, n_jobs=-1, scoring='f1')),
        }

    def save(self, target_folder):
        target_path = os.path.join(target_folder, 'joblib')
        joblib.dump(self.model, target_path)
        return self.variables


def load_prepared_arrays_and_labels(dataset_path):
    return dataset.load_arrays_and_labels(flatten(dataset_path))
