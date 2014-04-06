import numpy as np
import rtree
import scipy.spatial.kdtree


class KDTree(object):

    def __init__(self, points):
        points = np.array(points)
        self.point_count = len(points)
        self.kdtree = scipy.spatial.kdtree.KDTree(points)

    def query(self, x, maximum_count=None, maximum_distance=None):
        x = np.array(x)
        if x.ndim == 1:
            x = np.array([x])
        distances, indices = self.kdtree.query(
            x,
            k=maximum_count or self.point_count,
            distance_upper_bound=maximum_distance or np.inf)
        try:
            distances = distances[distances != np.inf]
            indices = indices[indices != self.point_count]
            return distances, indices
        except (TypeError, IndexError):
            return distances, indices


class RTree(object):

    def __init__(self, points):
        self.rtree = rtree.index.Index()
        for index, point in enumerate(points):
            self.rtree.insert(index, tuple(point))

    def intersects(self, bounds):
        try:
            self.rtree.intersection(bounds).next()
        except StopIteration:
            return False
        else:
            return True
