import random
import unittest
import pandas as pd
from datetime import datetime
from model.trafficHistory import TrafficHistoryModel
from model.boder import BordeModel
from model.bras import BrasModel
from model.caching import CachingModel
from model.rai import RaiModel
from handler.traffic import TrafficHandler
from test import DatabasePostgresTest, DatabaseMongoTest, LayerTypeTest, ModelBordeTypeTest, BrasTypeTest


class TestMongoTrafficHandler(unittest.TestCase):
    test_database: DatabaseMongoTest = DatabaseMongoTest()
    test_interface_borde: BordeModel = BordeModel(
        id=None,
        name="interface_test_" + str(random.randint(0, 1000)),
        model=ModelBordeTypeTest.CISCO,
        capacity=10,
        createAt=datetime.now().strftime("%Y-%m-%d")
    )
    test_interface_bras: BrasModel = BrasModel(
        id=None,
        name="interface_test_" + str(random.randint(0, 1000)),
        type=BrasTypeTest.UPLINK,
        capacity=10,
        createAt=datetime.now().strftime("%Y-%m-%d")
    )
    test_interface_caching: CachingModel = CachingModel(
        id=None,
        name="interface_test_" + str(random.randint(0, 1000)),
        service="service_test_" + str(random.randint(0, 1000)),
        capacity=10,
        createAt=datetime.now().strftime("%Y-%m-%d")
    )
    test_interface_rai: RaiModel = RaiModel(
        id=None,
        name="interface_test_" + str(random.randint(0, 1000)),
        capacity=10,
        createAt=datetime.now().strftime("%Y-%m-%d")
    )
    test_traffic: TrafficHistoryModel = TrafficHistoryModel(
        date=datetime.now().strftime("%Y-%m-%d"),
        time="00:00:00",
        inProm=20,
        inMax=30,
        outProm=20,
        outMax=30,
        idLayer="",
        typeLayer=LayerTypeTest.BORDE
    )

    def test_get_traffic_interface_by_date(self):
        """Test get all traffic history of a interface by date with MongoDB."""
        interface_borde = self.test_database.insert(table=LayerTypeTest.BORDE, data=self.test_interface_borde.model_dump())
        self.test_traffic.idLayer = str(interface_borde["_id"])
        self.test_database.insert(table=LayerTypeTest.TRAFFIC_HISTORY, data=self.test_traffic.model_dump())

        trafficHandler = TrafficHandler()
        data_traffic = trafficHandler.get_traffic_interface_by_date(
            layer_type=self.test_traffic.typeLayer,
            interface_name=self.test_interface_borde.name,
            date=self.test_traffic.date
        )
        self.test_database.clean(table=LayerTypeTest.BORDE)
        self.test_database.clean(table=LayerTypeTest.TRAFFIC_HISTORY)

        self.assertIsNotNone(data_traffic)
        self.assertEqual(type(data_traffic), pd.DataFrame)
        self.assertFalse(data_traffic.empty)

    def test_get_traffic_layer_by_date(self):
        """Test get all traffic history of a layer by a date with MongoDB."""
        interface = self.test_database.insert(table=LayerTypeTest.BORDE, data=self.test_interface_borde.model_dump())
        self.test_traffic.idLayer = str(interface["_id"])
        self.test_database.insert(table=LayerTypeTest.TRAFFIC_HISTORY, data=self.test_traffic.model_dump())

        trafficHandler = TrafficHandler()
        data_traffic = trafficHandler.get_traffic_layer_by_date(
            layer_type=self.test_traffic.typeLayer,
            date=self.test_traffic.date
        )
        self.test_database.clean(table=LayerTypeTest.BORDE)
        self.test_database.clean(table=LayerTypeTest.TRAFFIC_HISTORY)
        
        self.assertIsNotNone(data_traffic)
        self.assertEqual(type(data_traffic), pd.DataFrame)
        self.assertFalse(data_traffic.empty)

if __name__ == "__main__":
    unittest.main()