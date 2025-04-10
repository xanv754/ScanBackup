import unittest
from updater.handler.rai import RaiUpdaterHandler

class TestHistoryUpdater(unittest.TestCase):
    def test_get_data(self):
        """Test get all data from rai files."""
        raiHandler = RaiUpdaterHandler()
        data = raiHandler.get_data()
        self.assertEqual(type(data), list)
        self.assertTrue(data)


if __name__ == "__main__":
    unittest.main()
