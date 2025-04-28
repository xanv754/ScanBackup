import unittest
from updater.handler.bras import BrasUpdaterHandler
from test import FileBrasDataTest, BrasTypeTest


class TestHistoryUpdater(unittest.TestCase):
    def test_get_data(self):
        """Test get all data from bras files."""
        data_example = FileBrasDataTest(filename=f"{BrasTypeTest.UPLINK}%INTERFACE_TEST_1%10")
        data_example.create_file()
        brasHandler = BrasUpdaterHandler()
        data = brasHandler.get_data(filepath=data_example.folder)
        data_example.delete_file()
        data_example.delete_father_folder()
        
        self.assertEqual(type(data), list)
        self.assertTrue(data)


if __name__ == "__main__":
    unittest.main()
