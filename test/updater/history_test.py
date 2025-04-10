import unittest
import os
from constants.path import PathConstant
from updater.handler.history import HistoryUpdaterHandler

class TestHistoryUpdater(unittest.TestCase):
    def test_get_data(self):
        """Test to get data from history files."""
        if os.path.exists(PathConstant.SCAN_DATA_BORDER) and os.path.isdir(PathConstant.SCAN_DATA_BORDER):
            files = [filename for filename in os.listdir(PathConstant.SCAN_DATA_BORDER)]
            filepath = f"{PathConstant.SCAN_DATA_BORDER}/{files[0]}"
            historyHandler = HistoryUpdaterHandler()
            data = historyHandler.get_data(filepath=filepath)
            self.assertEqual(type(data), list)
            self.assertTrue(data)
        else:
            self.assertTrue(False)


if __name__ == "__main__":
    unittest.main()