import unittest
from database import MongoTrafficHistoryQuery, PostgresTrafficHistoryQuery
from model import TrafficHistoryFieldModel
from test import DatabaseTrafficTest


class Query(unittest.TestCase):
    mongo_db_test: DatabaseTrafficTest = DatabaseTrafficTest()
    postgres_db_test: DatabaseTrafficTest = DatabaseTrafficTest(db_backup=True)

    def test_insert(self):
        """Test insert a new traffic of a layer in the database."""
        new_traffic = self.mongo_db_test.get_exampĺe()
        database = MongoTrafficHistoryQuery(uri=self.mongo_db_test.uri)
        response = database.new_traffic(traffic=[new_traffic])
        self.mongo_db_test.clean()
        self.assertTrue(response)

        new_traffic = self.postgres_db_test.get_exampĺe()
        database = PostgresTrafficHistoryQuery(uri=self.postgres_db_test.uri)
        response = database.new_traffic(traffic=[new_traffic])
        self.postgres_db_test.clean()

    def test_get(self):
        """Test get a traffic of a layer in the database."""
        example_traffic = self.mongo_db_test.insert()
        database = MongoTrafficHistoryQuery(uri=self.mongo_db_test.uri)
        response = database.get_traffic(
            date=example_traffic.date, 
            time=example_traffic.time, 
            id_layer=example_traffic.idLayer
        )
        print(response)
        self.mongo_db_test.clean()
        self.assertFalse(response.empty)
        self.assertEqual(response[TrafficHistoryFieldModel.date].iloc[0], example_traffic.date)
        self.assertEqual(response[TrafficHistoryFieldModel.time].iloc[0], example_traffic.time)
        self.assertEqual(str(response[TrafficHistoryFieldModel.idLayer].iloc[0]), example_traffic.idLayer)

        example_traffic = self.postgres_db_test.insert()
        database = PostgresTrafficHistoryQuery(uri=self.postgres_db_test.uri)
        response = database.get_traffic(
            date=example_traffic.date, 
            time=example_traffic.time, 
            id_layer=example_traffic.idLayer
        )
        print(response)
        self.postgres_db_test.clean()
        self.assertFalse(response.empty)
        self.assertEqual(response[TrafficHistoryFieldModel.date].iloc[0], example_traffic.date)
        self.assertEqual(response[TrafficHistoryFieldModel.time].iloc[0], example_traffic.time)
        self.assertEqual(str(response[TrafficHistoryFieldModel.idLayer].iloc[0]), example_traffic.idLayer)

    def test_get_by_layer_and_date(self):
        """Test get all traffic history of a type layer by date in database."""
        example_traffic = self.mongo_db_test.insert()
        database = MongoTrafficHistoryQuery(uri=self.mongo_db_test.uri)
        interface = database.get_traffic_layer_by_date(
            layer_type=example_traffic.typeLayer, 
            date=example_traffic.date
        )
        print(interface)
        self.mongo_db_test.clean()
        self.assertFalse(interface.empty)
        self.assertEqual(interface[TrafficHistoryFieldModel.date].iloc[0], example_traffic.date)
        self.assertEqual(interface[TrafficHistoryFieldModel.typeLayer].iloc[0], example_traffic.typeLayer)

        example_traffic = self.postgres_db_test.insert()
        database = PostgresTrafficHistoryQuery(uri=self.postgres_db_test.uri)
        interface = database.get_traffic_layer_by_date(
            layer_type=example_traffic.typeLayer, 
            date=example_traffic.date
        )
        print(interface)
        self.postgres_db_test.clean()
        self.assertFalse(interface.empty)
        self.assertEqual(interface[TrafficHistoryFieldModel.date].iloc[0], example_traffic.date)


if __name__ == "__main__":
    unittest.main()