import unittest

from ..scripts.get_dataset_from_examples import adjust_counts


class ScriptTest(unittest.TestCase):

    def test_adjust_counts(self):
        self.assertEqual((100, 1000), adjust_counts(
            positive_count=100,
            negative_count=1000,
            maximum_dataset_size=None,
            positive_fraction=None,
            batch_size=None))
        self.assertEqual((100, 100), adjust_counts(
            positive_count=100,
            negative_count=1000,
            maximum_dataset_size=200,
            positive_fraction=None,
            batch_size=None))
        self.assertEqual((100, 100), adjust_counts(
            positive_count=100,
            negative_count=1000,
            maximum_dataset_size=None,
            positive_fraction=0.5,
            batch_size=None))
        self.assertEqual((9, 90), adjust_counts(
            positive_count=100,
            negative_count=1000,
            maximum_dataset_size=100,
            positive_fraction=-1,
            batch_size=None))


if __name__ == '__main__':
    unittest.main()
