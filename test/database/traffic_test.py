import random
import unittest
from unittest.mock import MagicMock
from constants.group import LayerType
from model.trafficHistory import TrafficHistoryModel
from database.querys.traffic.mongo import MongoTrafficHistoryQuery
from database.querys.traffic.postgres import PostgresTrafficHistoryQuery


class TestTrafficHistoryOperation(unittest.TestCase):
    def test_insert_traffic(self):
        """Test insert a new traffic of a layer in the database."""
        mock_traffic = MagicMock()
        mock_traffic.traffic_history_model.return_value = TrafficHistoryModel(
            date="2025-04-01",
            time="00:00:00",
            inProm=0,
            inMax=0,
            outProm=0,
            outMax=0,
            idLayer=str(random.randint(0, 1000)),
            typeLayer=LayerType.BORDE
        )
        database = MongoTrafficHistoryQuery()
        
        response = database.new_traffic(traffic=[mock_traffic.traffic_history_model()])
        self.assertTrue(response)

    def test_insert_traffic_postgres(self):
        """Test insert a new traffic of a layer in the database."""
        mock_traffic = MagicMock()
        mock_traffic.traffic_history_model.return_value = TrafficHistoryModel(
            date="2025-04-01",
            time="00:00:00",
            inProm=0,
            inMax=0,
            outProm=0,
            outMax=0,
            idLayer=str(random.randint(0, 1000)),
            typeLayer=LayerType.BORDE
        )
        database = PostgresTrafficHistoryQuery()
        
        response = database.new_traffic(traffic=[mock_traffic.traffic_history_model()])
        self.assertTrue(response)

if __name__ == "__main__":
    unittest.main()