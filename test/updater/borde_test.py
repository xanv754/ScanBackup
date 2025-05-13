import unittest
from database.constant.fields import BordeFieldDatabase
from updater import BordeUpdaterHandler
from test import FileBordeDataTest, DatabaseMongoTest, DatabasePostgresTest, LayerTypeTest, ModelBordeTypeTest


class TestHistoryUpdater(unittest.TestCase):
    test_database_mongo: DatabaseMongoTest = DatabaseMongoTest()
    test_database_postgres: DatabasePostgresTest = DatabasePostgresTest()

    def test_get_data(self):
        """Test get all data from border files."""
        data_example = FileBordeDataTest(filename=f"{ModelBordeTypeTest.CISCO}%INTERFACE_TEST_1%10")
        data_example.create_file()
        borderHandler = BordeUpdaterHandler()
        data = borderHandler.get_data(filepath=data_example.folder)
        data_example.delete_file()
        data_example.delete_father_folder()
        
        self.assertEqual(type(data), list)
        self.assertTrue(data)

    def test_load_data(self):
        """Test load all data from border files."""
        data_example = FileBordeDataTest(filename=f"{ModelBordeTypeTest.CISCO}%INTERFACE_TEST_1%10")
        data_example.create_file()
        borderHandler = BordeUpdaterHandler()
        data = borderHandler.get_data(filepath=data_example.folder)
        response = borderHandler.load_data(data=data)
        borde_records = self.test_database_mongo.get(table=LayerTypeTest.BORDE, condition={BordeFieldDatabase.NAME: "INTERFACE_TEST_1"})

        data_example.delete_file()
        data_example.delete_father_folder()
        self.test_database_mongo.clean(table=LayerTypeTest.BORDE)
        self.test_database_mongo.clean(table=LayerTypeTest.TRAFFIC_HISTORY)
        self.test_database_postgres.clean(table=LayerTypeTest.BORDE)
        self.test_database_postgres.clean(table=LayerTypeTest.TRAFFIC_HISTORY)

        self.assertTrue(response)
        self.assertEqual(len(borde_records), 1)
        self.assertEqual(borde_records[0][BordeFieldDatabase.NAME], "INTERFACE_TEST_1")
    

if __name__ == "__main__":
    unittest.main()