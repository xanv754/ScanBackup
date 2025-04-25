import unittest
from updater.handler.borde import BordeUpdaterHandler
from test import FileBordeDataTest


class TestHistoryUpdater(unittest.TestCase):
    def test_get_data(self):
        """Test get all data from border files."""
        data_example = FileBordeDataTest(filename="CISCO%INTERFACE_TEST_1%10")
        data_example.create_file()
        borderHandler = BordeUpdaterHandler()
        data = borderHandler.get_data(filepath=data_example.folder)
        self.assertEqual(type(data), list)
        self.assertTrue(data)
        data_example.delete_file()
        data_example.delete_father_folder()


if __name__ == "__main__":
    unittest.main()