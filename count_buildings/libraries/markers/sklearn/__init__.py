import joblib
import numpy as np
import os
from sklearn.cross_validation import cross_val_score

from .. import AbstractMarker
from ... import dataset
from ...preparations.flat import flatten


class ScikitLearnMarker(AbstractMarker):

    filename = 'joblib'

    def calibrate(self, dataset_path):
        arrays, labels = dataset.load_arrays_and_labels(flatten(dataset_path))
        self.model = self.Model()
        self.model.fit(arrays, labels)

    def cross_validate(self, dataset_path):
        arrays, labels = dataset.load_arrays_and_labels(flatten(dataset_path))
        return {
            'f1': np.mean(cross_val_score(
                self.Model(), arrays, labels, n_jobs=-1, scoring='f1')),
        }

    def scan(self, arrays_path):
        arrays = dataset.load_arrays(flatten(arrays_path))
        return [self.model.predict(_)[0] for _ in arrays]

    def save(self, target_folder):
        joblib.dump(self.model, os.path.join(target_folder, self.filename))
        return self.variables

    def load(self, source_folder):
        self.model = joblib.load(os.path.join(source_folder, self.filename))
        return self
