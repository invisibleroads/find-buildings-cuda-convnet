from sklearn.svm import SVC

from . import ScikitLearnMarker


class Marker(ScikitLearnMarker):

    Model = SVC
