import unittest
import random
from datetime import datetime
from constants.header import HeaderDataFrame
from controllers import SummaryController
from model import BordeModel, TrafficHistoryModel
from test import DatabaseMongoTest, DatabasePostgresTest, LayerTypeTest, ModelBordeTypeTest


def get_example_interface_borde() -> BordeModel:
    """Get example interface of borde layer."""
    return BordeModel(
        id=str(random.randint(0, 1000)),
        name="interface_test_" + str(random.randint(0, 1000)),
        model=ModelBordeTypeTest.CISCO,
        capacity=10,
        createAt=datetime.now().strftime("%Y-%m-%d")
    )

def get_example_interface_traffic() -> TrafficHistoryModel:
    """Get example interface of traffic history of borde layer."""
    return TrafficHistoryModel(
        date=datetime.now().strftime("%Y-%m-%d"),
        time="00:00:00",
        inProm=random.randint(10, 20),
        inMax=random.randint(10, 40),
        outProm=random.randint(10, 20),
        outMax=random.randint(10, 40),
        idLayer="",
        typeLayer=""
    )


class TestController(unittest.TestCase):
    test_database: DatabaseMongoTest = DatabaseMongoTest()

    def insert_borde_traffic(self) -> None:
        """Insert data example in the TrafficHistory table in the MongoDB."""
        example_interface_one = get_example_interface_borde()
        example_traffic_one = get_example_interface_traffic()
        interface_one = self.test_database.insert(table=LayerTypeTest.BORDE, data=example_interface_one.model_dump())
        example_traffic_one.idLayer = str(interface_one["_id"])
        example_traffic_one.typeLayer = LayerTypeTest.BORDE
        self.test_database.insert(table=LayerTypeTest.TRAFFIC_HISTORY, data=example_traffic_one.model_dump())
        example_interface_two = get_example_interface_borde()
        example_traffic_two = get_example_interface_traffic()
        interface_two = self.test_database.insert(table=LayerTypeTest.BORDE, data=example_interface_two.model_dump())
        example_traffic_two.idLayer = str(interface_two["_id"])
        example_traffic_two.typeLayer = LayerTypeTest.BORDE
        self.test_database.insert(table=LayerTypeTest.TRAFFIC_HISTORY, data=example_traffic_two.model_dump())


    def test_get_summary_diary(self):
        """Test get summary diary of borde layer."""
        self.insert_borde_traffic()
        data = SummaryController.summary_diary_current()
        df_data_borde = data[LayerTypeTest.BORDE]
        df_data_columns = df_data_borde.columns.to_list()
        neccesary_columns = [
            HeaderDataFrame.INTERFACE,
            HeaderDataFrame.TYPE,
            HeaderDataFrame.CAPACITY,
            HeaderDataFrame.IN_PROM,
            HeaderDataFrame.OUT_PROM,
            HeaderDataFrame.IN_MAX_PROM,
            HeaderDataFrame.OUT_MAX_PROM,
            HeaderDataFrame.USE
        ]
        self.test_database.clean(table=LayerTypeTest.BORDE)
        self.test_database.clean(table=LayerTypeTest.TRAFFIC_HISTORY)

        self.assertFalse(df_data_borde.empty)
        self.assertEqual(df_data_columns, neccesary_columns)



if __name__ == "__main__":
    unittest.main()