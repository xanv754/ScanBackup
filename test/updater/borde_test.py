import unittest
from database.constant.fields import BordeFieldDatabase
from updater.handler.borde import BordeUpdaterHandler
from test import FileBordeDataTest, DatabaseMongoTest


class TestHistoryUpdater(unittest.TestCase):
    test_database: DatabaseMongoTest = DatabaseMongoTest()

    def test_get_data(self):
        """Test get all data from border files."""
        data_example = FileBordeDataTest(filename="CISCO%INTERFACE_TEST_1%10")
        data_example.create_file()
        borderHandler = BordeUpdaterHandler()
        data = borderHandler.get_data(filepath=data_example.folder)
        data_example.delete_file()
        data_example.delete_father_folder()
        
        self.assertEqual(type(data), list)
        self.assertTrue(data)

    def test_load_data(self):
        """Test load all data from border files."""
        data_example = FileBordeDataTest(filename="CISCO%INTERFACE_TEST_1%10")
        data_example.create_file()
        borderHandler = BordeUpdaterHandler()
        data = borderHandler.get_data(filepath=data_example.folder)
        response = borderHandler.load_data(data=data)
        borde_records = self.test_database.get(table=data_example.folder, condition={BordeFieldDatabase.NAME: "INTERFACE_TEST_1"})
    
        data_example.delete_file()
        data_example.delete_father_folder()

        self.assertTrue(response)
    




if __name__ == "__main__":
    unittest.main()