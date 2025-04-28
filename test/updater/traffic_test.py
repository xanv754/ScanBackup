import unittest
from updater.handler.traffic import TrafficHistoryUpdaterHandler
from test import FileCachingDataTest


class TestTrafficHistoryUpdater(unittest.TestCase):
    def test_get_data(self):
        """Test to get data from history files."""
        data_example = FileCachingDataTest(filename="SERVICIO%INTERFACE_TEST_1%22.5")
        data_example.create_file()
        historyHandler = TrafficHistoryUpdaterHandler()
        data = historyHandler.get_data(filepath=data_example.filepath)
        data_example.delete_file()
        data_example.delete_father_folder()
        
        self.assertEqual(type(data), list)
        self.assertTrue(data)


if __name__ == "__main__":
    unittest.main()
