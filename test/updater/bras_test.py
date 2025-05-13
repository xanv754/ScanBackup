import unittest
from database import BrasFieldDatabase
from updater import BrasUpdaterHandler
from test import FileBrasDataTest, DatabaseMongoTest, DatabasePostgresTest, BrasTypeTest, LayerTypeTest


class TestHistoryUpdater(unittest.TestCase):
    test_database_mongo: DatabaseMongoTest = DatabaseMongoTest()
    test_database_postgres: DatabasePostgresTest = DatabasePostgresTest()

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

    def test_load_data(self):
        """Test load all data from border files."""
        data_example = FileBrasDataTest(filename=f"{BrasTypeTest.UPLINK}%INTERFACE_TEST_1%10")
        data_example.create_file()
        brasHandler = BrasUpdaterHandler()
        data = brasHandler.get_data(filepath=data_example.folder)
        response = brasHandler.load_data(data=data)
        bras_records = self.test_database_mongo.get(table=LayerTypeTest.BRAS, condition={BrasFieldDatabase.NAME: "INTERFACE_TEST_1"})

        data_example.delete_file()
        data_example.delete_father_folder()
        self.test_database_mongo.clean(table=LayerTypeTest.BRAS)
        self.test_database_mongo.clean(table=LayerTypeTest.TRAFFIC_HISTORY)
        self.test_database_postgres.clean(table=LayerTypeTest.BRAS)
        self.test_database_postgres.clean(table=LayerTypeTest.TRAFFIC_HISTORY)

        self.assertTrue(response)
        self.assertEqual(len(bras_records), 1)
        self.assertEqual(bras_records[0][BrasFieldDatabase.NAME], "INTERFACE_TEST_1")


if __name__ == "__main__":
    unittest.main()
