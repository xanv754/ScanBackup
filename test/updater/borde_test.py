import unittest
from updater.handler.borde import BordeUpdaterHandler


class TestHistoryUpdater(unittest.TestCase):
    def test_get_data(self):
        """Test get all data from border files."""
        borderHandler = BordeUpdaterHandler()
        data = borderHandler.get_data()
        self.assertEqual(type(data), list)
        self.assertTrue(data)


if __name__ == "__main__":
    unittest.main()