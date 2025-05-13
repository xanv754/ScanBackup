import unittest
import random
from database import TrafficHistoryFieldDatabase
from updater import TrafficHistoryUpdaterHandler
from test import FileCachingDataTest, DatabaseMongoTest, DatabasePostgresTest, LayerTypeTest


class TestTrafficHistoryUpdater(unittest.TestCase):
    test_database_mongo: DatabaseMongoTest = DatabaseMongoTest()
    test_database_postgres: DatabasePostgresTest = DatabasePostgresTest()

    def test_get_data(self):
        """Test to get data from history files."""
        data_example = FileCachingDataTest(filename="SERVICE%INTERFACE_TEST_1%22.5")
        data_example.create_file()
        historyHandler = TrafficHistoryUpdaterHandler()
        data = historyHandler.get_data(filepath=data_example.filepath)
        data_example.delete_file()
        data_example.delete_father_folder()
        
        self.assertEqual(type(data), list)
        self.assertTrue(data)

    def test_load_data(self):
        """Test load all data from border files."""
        data_example = FileCachingDataTest(filename="SERVICE%INTERFACE_TEST_1%22.5")
        data_example.create_file()
        trafficHandler = TrafficHistoryUpdaterHandler()
        data = trafficHandler.get_data(filepath=data_example.filepath)
        for data_traffic in data:
            data_traffic.idLayer = str(random.randint(0, 1000))
            data_traffic.typeLayer = LayerTypeTest.CACHING

        response = trafficHandler.load_data(data=data, mongo=True)
        traffic_records = self.test_database_mongo.get(table=LayerTypeTest.TRAFFIC_HISTORY, condition={TrafficHistoryFieldDatabase.ID_LAYER: data[0].idLayer})

        data_example.delete_file()
        data_example.delete_father_folder()
        self.test_database_mongo.clean(table=LayerTypeTest.CACHING)
        self.test_database_mongo.clean(table=LayerTypeTest.TRAFFIC_HISTORY)
        self.test_database_postgres.clean(table=LayerTypeTest.CACHING)
        self.test_database_postgres.clean(table=LayerTypeTest.TRAFFIC_HISTORY)

        self.assertTrue(response)
        self.assertEqual(len(traffic_records), 1)
        self.assertEqual(traffic_records[0][TrafficHistoryFieldDatabase.ID_LAYER], data[0].idLayer)

if __name__ == "__main__":
    unittest.main()
