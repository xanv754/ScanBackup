import unittest
from updater.handler.rai import RaiUpdaterHandler
from test import FileRaiDataTest

class TestHistoryUpdater(unittest.TestCase):
    def test_get_data(self):
        """Test get all data from rai files."""
        data_example = FileRaiDataTest(filename="DEDICADO%INTERFACE_TEST_1%0.04")
        data_example.create_file()
        raiHandler = RaiUpdaterHandler()
        data = raiHandler.get_data(filepath=data_example.folder)
        data_example.delete_file()
        data_example.delete_father_folder()
        
        self.assertEqual(type(data), list)
        self.assertTrue(data)


if __name__ == "__main__":
    unittest.main()
