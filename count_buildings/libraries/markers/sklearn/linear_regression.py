from sklearn.externals import joblib
from sklearn.linear_model import LinearRegression


class Marker(object):

    def __init__(self, target_folder):
        self.target_folder = target_folder

    def calibrate(self, arrays, labels):
        processed_arrays = [_.flatten() for _ in arrays]
        self.model = LinearRegression()
        self.model.fit(processed_arrays, labels)

    def save(self, target_folder):
        target_path = os.path.join(target_folder, 'joblib')
        joblib.dump(self.model, target_path)


