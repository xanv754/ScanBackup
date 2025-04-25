import random
import unittest
import pandas as pd
from datetime import datetime
from model.trafficHistory import TrafficHistoryModel
from model.boder import BordeModel
from handler.traffic import TrafficHandler
from test import DatabasePostgresTest, DatabaseMongoTest, LayerTypeTest, ModelBordeTypeTest, TrafficFieldDatabaseTest


class TestMongoTrafficHandler(unittest.TestCase):
    test_database: DatabaseMongoTest = DatabaseMongoTest()
    test_interface: BordeModel = BordeModel(
        id=None,
        name="interface_test_" + str(random.randint(0, 1000)),
        model=ModelBordeTypeTest.CISCO,
        capacity=0,
        createAt=datetime.now().strftime("%Y-%m-%d")
    )
    test_traffic: TrafficHistoryModel = TrafficHistoryModel(
        date=datetime.now().strftime("%Y-%m-%d"),
        time="00:00:00",
        inProm=0,
        inMax=0,
        outProm=0,
        outMax=0,
        idLayer="",
        typeLayer=LayerTypeTest.BORDE
    )

    def test_get_traffic_interface_by_date(self):
        """Test get all traffic history of a interface by date with MongoDB."""
        interface = self.test_database.insert(table=LayerTypeTest.BORDE, data=self.test_interface.model_dump())
        self.test_traffic.idLayer = str(interface["_id"])
        self.test_database.insert(table=LayerTypeTest.TRAFFIC_HISTORY, data=self.test_traffic.model_dump())

        trafficHandler = TrafficHandler()
        data_traffic = trafficHandler.get_traffic_interface_by_date(
            layer_type=self.test_traffic.typeLayer,
            interface_name=self.test_interface.name,
            date=self.test_traffic.date
        )
        self.assertIsNotNone(data_traffic)
        self.assertEqual(type(data_traffic), pd.DataFrame)
        self.assertFalse(data_traffic.empty)
        self.test_database.clean(table=LayerTypeTest.BORDE)
        self.test_database.clean(table=LayerTypeTest.TRAFFIC_HISTORY)

    def test_get_traffic_layer_by_date(self):
        """Test get all traffic history of a layer by a date with MongoDB."""
        interface = self.test_database.insert(table=LayerTypeTest.BORDE, data=self.test_interface.model_dump())
        self.test_traffic.idLayer = str(interface["_id"])
        self.test_database.insert(table=LayerTypeTest.TRAFFIC_HISTORY, data=self.test_traffic.model_dump())

        trafficHandler = TrafficHandler()
        data_traffic = trafficHandler.get_traffic_layer_by_date(
            layer_type=self.test_traffic.typeLayer,
            date=self.test_traffic.date
        )
        self.assertIsNotNone(data_traffic)
        self.assertEqual(type(data_traffic), pd.DataFrame)
        self.assertFalse(data_traffic.empty)
        self.test_database.clean(table=LayerTypeTest.BORDE)
        self.test_database.clean(table=LayerTypeTest.TRAFFIC_HISTORY)

if __name__ == "__main__":
    unittest.main()