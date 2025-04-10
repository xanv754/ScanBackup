import os
import unittest
from dotenv import load_dotenv
from model.trafficHistory import TrafficHistoryModel
from storage.querys.history.mongo import MongoHistoryTrafficQuery


load_dotenv(override=True)

URI_TEST_MONGO = os.getenv("URI_MONGO")
TRAFFIC_EXAMPLE = TrafficHistoryModel(
    date="2025-01-01",
    time="12:00:00",
    idLayer="interface_test",
    typeLayer="Borde",
    inProm=0,
    inMax=0,
    outProm=0,
    outMax=0
)


class TestHistoryTraffic(unittest.TestCase):
    def test_insert_traffic(self):
        """Test insert a new traffic of a layer in the database."""
        database = MongoHistoryTrafficQuery()
        database.set_database(uri=URI_TEST_MONGO)
        response = database.new_histories(new_histories=[TRAFFIC_EXAMPLE])
        self.assertTrue(response)

    def test_get_all_traffic_by_layer(self):
        database = MongoHistoryTrafficQuery()
        database.set_database(uri=URI_TEST_MONGO)
        response = database.get_all_traffic_by_layer(layer_name=TRAFFIC_EXAMPLE.typeLayer)
        self.assertTrue(response)
        self.assertEqual(response[0].idLayer, TRAFFIC_EXAMPLE.idLayer)

if __name__ == "__main__":
    unittest.main()