import unittest
from database import RaiFieldDatabase
from updater import RaiUpdaterHandler
from test import FileRaiDataTest, DatabaseMongoTest, DatabasePostgresTest, LayerTypeTest

class TestHistoryUpdater(unittest.TestCase):
    test_database_mongo: DatabaseMongoTest = DatabaseMongoTest()
    test_database_postgres: DatabasePostgresTest = DatabasePostgresTest()

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

    def test_load_data(self):
        """Test load all data from border files."""
        data_example = FileRaiDataTest(filename="DEDICADO%INTERFACE_TEST_1%10")
        data_example.create_file()
        raiHandler = RaiUpdaterHandler()
        data = raiHandler.get_data(filepath=data_example.folder)
        response_mongo = raiHandler._load_database(data=data)
        response_postgres = raiHandler._load_database(data=data, db_backup=True)
        if response_mongo and response_postgres: response = True
        else: response = False
        rai_records = self.test_database_mongo.get(table=LayerTypeTest.RAI, condition={RaiFieldDatabase.NAME: "INTERFACE_TEST_1"})

        data_example.delete_file()
        data_example.delete_father_folder()
        self.test_database_mongo.clean(table=LayerTypeTest.RAI)
        self.test_database_mongo.clean(table=LayerTypeTest.TRAFFIC_HISTORY)
        self.test_database_postgres.clean(table=LayerTypeTest.RAI)
        self.test_database_postgres.clean(table=LayerTypeTest.TRAFFIC_HISTORY)

        self.assertTrue(response)
        self.assertEqual(len(rai_records), 1)
        self.assertEqual(rai_records[0][RaiFieldDatabase.NAME], "INTERFACE_TEST_1")


if __name__ == "__main__":
    unittest.main()
