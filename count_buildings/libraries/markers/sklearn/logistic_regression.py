from sklearn.linear_model import LogisticRegression

from . import ScikitLearnMarker


class Marker(ScikitLearnMarker):

    Model = LogisticRegression
