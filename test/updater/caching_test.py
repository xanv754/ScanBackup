import unittest
from database import CachingFieldDatabase
from updater import CachingUpdaterHandler
from test import FileCachingDataTest, DatabaseMongoTest, DatabasePostgresTest, LayerTypeTest


class TestHistoryUpdater(unittest.TestCase):
    test_database_mongo: DatabaseMongoTest = DatabaseMongoTest()
    test_database_postgres: DatabasePostgresTest = DatabasePostgresTest()

    def test_get_data(self):
        """Test get all data from caching files."""
        data_example = FileCachingDataTest(filename="SERVICE%INTERFACE_TEST_1%22.5")
        data_example.create_file()
        cachingHandler = CachingUpdaterHandler()
        data = cachingHandler.get_data(filepath=data_example.folder)
        data_example.delete_file()
        data_example.delete_father_folder()
        
        self.assertEqual(type(data), list)
        self.assertTrue(data)

    def test_load_data(self):
        """Test load all data from border files."""
        data_example = FileCachingDataTest(filename="SERVICE%INTERFACE_TEST_1%10")
        data_example.create_file()
        cachingHandler = CachingUpdaterHandler()
        data = cachingHandler.get_data(filepath=data_example.folder)
        response_mongo = cachingHandler._load_database(data=data)
        response_postgres = cachingHandler._load_database(data=data, db_backup=True)
        if response_mongo and response_postgres: response = True
        else: response = False
        caching_records = self.test_database_mongo.get(table=LayerTypeTest.CACHING, condition={CachingFieldDatabase.NAME: "INTERFACE_TEST_1"})

        data_example.delete_file()
        data_example.delete_father_folder()
        self.test_database_mongo.clean(table=LayerTypeTest.CACHING)
        self.test_database_mongo.clean(table=LayerTypeTest.TRAFFIC_HISTORY)
        self.test_database_postgres.clean(table=LayerTypeTest.CACHING)
        self.test_database_postgres.clean(table=LayerTypeTest.TRAFFIC_HISTORY)

        self.assertTrue(response)
        self.assertEqual(len(caching_records), 1)
        self.assertEqual(caching_records[0][CachingFieldDatabase.NAME], "INTERFACE_TEST_1")


if __name__ == "__main__":
    unittest.main()
