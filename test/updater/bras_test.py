import unittest
from updater.handler.bras import BrasUpdaterHandler


class TestHistoryUpdater(unittest.TestCase):
    def test_get_data(self):
        """Test get all data from bras files."""
        brasHandler = BrasUpdaterHandler()
        data = brasHandler.get_data()
        self.assertEqual(type(data), list)
        self.assertTrue(data)


if __name__ == "__main__":
    unittest.main()
