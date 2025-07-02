import unittest
from pandas import DataFrame
from updater import BordeUpdaterHandler
from test import FileBordeDataTest, DatabaseBorderTest

class Updater(unittest.TestCase):
    mongo_borde_db_test: DatabaseBorderTest = DatabaseBorderTest()
    data_example: FileBordeDataTest = FileBordeDataTest(filename=f"CISCO%INTERFACE_TEST_1%10")

    def clean(self):
        self.data_example.delete_file()
        self.mongo_borde_db_test.clean()

    def test_get_data(self):
        """Test get all data from border files."""
        self.data_example.create_file()

        borderHandler = BordeUpdaterHandler()
        data = borderHandler.get_data(folderpath=self.data_example.folder)
        print(data)
        self.clean()
        self.assertEqual(type(data), DataFrame)
        self.assertFalse(data.empty)

    def test_load_data(self):
        """Test load all data from border files."""
        self.data_example.create_file()

        borderHandler = BordeUpdaterHandler()
        data = borderHandler.get_data(folderpath=self.data_example.folder)
        status_operation = borderHandler.load_data(data=data, uri=self.mongo_borde_db_test.uri)
        self.assertTrue(status_operation)
        data_mongo = self.mongo_borde_db_test.get_all()
        self.assertEqual(len(data_mongo), 3)

        self.clean()
    

if __name__ == "__main__":
    unittest.main()