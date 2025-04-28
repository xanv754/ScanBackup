import unittest
from updater.handler.caching import CachingUpdaterHandler
from test import FileCachingDataTest


class TestHistoryUpdater(unittest.TestCase):
    def test_get_data(self):
        """Test get all data from caching files."""
        data_example = FileCachingDataTest(filename="SERVICIO%INTERFACE_TEST_1%22.5")
        data_example.create_file()
        cachingHandler = CachingUpdaterHandler()
        data = cachingHandler.get_data(filepath=data_example.folder)
        data_example.delete_file()
        data_example.delete_father_folder()
        
        self.assertEqual(type(data), list)
        self.assertTrue(data)


if __name__ == "__main__":
    unittest.main()
