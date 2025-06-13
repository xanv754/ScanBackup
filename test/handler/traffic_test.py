import unittest
from constants.header import HeaderDataFrame
from handler import TrafficHandler
from test import DatabaseTrafficTest


class Handler(unittest.TestCase):
    mongo_db_test: DatabaseTrafficTest = DatabaseTrafficTest()
    postgres_db_test: DatabaseTrafficTest = DatabaseTrafficTest(db_backup=True)

    def test_get_by_days_ago(self):
        """Test get all traffic history of a borde layer from a certain number of days ago."""
        neccesary_columns = [
            HeaderDataFrame.INTERFACE, HeaderDataFrame.TYPE, HeaderDataFrame.CAPACITY,
            HeaderDataFrame.DATE, HeaderDataFrame.TIME, HeaderDataFrame.IN_PROM, 
            HeaderDataFrame.OUT_PROM, HeaderDataFrame.IN_MAX, HeaderDataFrame.OUT_MAX
        ]

        example_traffic = self.mongo_db_test.insert()
        trafficHandler = TrafficHandler(uri=self.mongo_db_test.uri)
        data = trafficHandler.get_traffic_layer_by_days_ago(layer_type=example_traffic.typeLayer, day_before=1)
        print(data)
        data_columns = data.columns.to_list()
        self.mongo_db_test.clean(border=True)
        self.assertFalse(data.empty)
        self.assertEqual(data_columns, neccesary_columns)

        example_traffic = self.postgres_db_test.insert()
        trafficHandler = TrafficHandler(db_backup=True, uri=self.postgres_db_test.uri)
        data = trafficHandler.get_traffic_layer_by_days_ago(layer_type=example_traffic.typeLayer, day_before=1)
        print(data)
        data_columns = data.columns.to_list()
        self.postgres_db_test.clean(border=True)
        self.assertFalse(data.empty)
        self.assertEqual(data_columns, neccesary_columns)

    def test_get_by_day(self):
        """Test get all traffic history of a borde layer from a certain date."""
        neccesary_columns = [
            HeaderDataFrame.INTERFACE, HeaderDataFrame.TYPE, HeaderDataFrame.CAPACITY,
            HeaderDataFrame.DATE, HeaderDataFrame.TIME, HeaderDataFrame.IN_PROM, 
            HeaderDataFrame.OUT_PROM, HeaderDataFrame.IN_MAX, HeaderDataFrame.OUT_MAX
        ]

        example_traffic = self.mongo_db_test.insert()
        trafficHandler = TrafficHandler(uri=self.mongo_db_test.uri)
        data = trafficHandler.get_traffic_layer_by_day(layer_type=example_traffic.typeLayer, date=example_traffic.date)
        print(data)
        data_columns = data.columns.to_list()
        self.mongo_db_test.clean(border=True)
        self.assertFalse(data.empty)
        self.assertEqual(data_columns, neccesary_columns)

        example_traffic = self.postgres_db_test.insert()
        trafficHandler = TrafficHandler(db_backup=True, uri=self.postgres_db_test.uri)
        data = trafficHandler.get_traffic_layer_by_day(layer_type=example_traffic.typeLayer, date=example_traffic.date)
        print(data)
        data_columns = data.columns.to_list()
        self.postgres_db_test.clean(border=True)
        self.assertFalse(data.empty)
        self.assertEqual(data_columns, neccesary_columns)


if __name__ == "__main__":
    unittest.main()