import unittest
from updater.handler.caching import CachingUpdaterHandler


class TestHistoryUpdater(unittest.TestCase):
    def test_get_data(self):
        """Test get all data from caching files."""
        cachingHandler = CachingUpdaterHandler()
        data = cachingHandler.get_data()
        self.assertEqual(type(data), list)
        self.assertTrue(data)


if __name__ == "__main__":
    unittest.main()
