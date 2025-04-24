import random
import unittest
from datetime import datetime
from model.trafficHistory import TrafficHistoryModel
from database.querys.traffic.mongo import MongoTrafficHistoryQuery
from database.querys.traffic.postgres import PostgresTrafficHistoryQuery
from test import DatabasePostgresTest, DatabaseMongoTest, LayerTypeTest

class TestMongoTrafficOperation(unittest.TestCase):
    test_database: DatabaseMongoTest = DatabaseMongoTest()
    test_traffic: TrafficHistoryModel = TrafficHistoryModel(
        date=datetime.now().strftime("%Y-%m-%d"),
        time="00:00:00",
        inProm=0,
        inMax=0,
        outProm=0,
        outMax=0,
        idLayer=str(random.randint(0, 1000)),
        typeLayer=LayerTypeTest.BORDE
    )

    def test_insert_traffic(self):
        """Test insert a new traffic of a layer in the MongoDB."""
        database = MongoTrafficHistoryQuery()
        response = database.new_traffic(traffic=[self.test_traffic])
        self.assertTrue(response)
        self.test_database.clean(table=LayerTypeTest.TRAFFIC_HISTORY)

    def test_get_traffic(self):
        """Test get a traffic of a layer in the MongoDB."""
        self.test_database.insert(table=LayerTypeTest.TRAFFIC_HISTORY, data=self.test_traffic.model_dump())
        database = MongoTrafficHistoryQuery()
        response = database.get_traffic(
            date=self.test_traffic.date, 
            time=self.test_traffic.time, 
            id_layer=self.test_traffic.idLayer
        )
        self.assertIsNotNone(response)
        self.assertEqual(response.date, self.test_traffic.date)
        self.assertEqual(response.time, self.test_traffic.time)
        self.assertEqual(response.idLayer, self.test_traffic.idLayer)
        self.test_database.clean(table=LayerTypeTest.TRAFFIC_HISTORY)

    def test_get_traffic_layer_by_date_mongo(self):
        """Test get all traffic history of a layer by date in mongo database."""
        self.test_database.insert(table=LayerTypeTest.TRAFFIC_HISTORY, data=self.test_traffic.model_dump())
        database = MongoTrafficHistoryQuery()
        interface = database.get_traffic_layer_by_date(
            id_layer=self.test_traffic.idLayer, 
            date=self.test_traffic.date
        )
        self.assertIsNotNone(interface)
        self.assertEqual(interface[0].date, self.test_traffic.date)
        self.assertEqual(interface[0].idLayer, self.test_traffic.idLayer)
        self.test_database.clean(table=LayerTypeTest.TRAFFIC_HISTORY)


if __name__ == "__main__":
    unittest.main()