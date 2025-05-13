import random
import unittest
from datetime import datetime
from constants import HeaderDataFrame
from database import TrafficHistoryFieldDatabase, BordeFieldDatabase, BrasFieldDatabase, CachingFieldDatabase, RaiFieldDatabase
from model import TrafficHistoryModel, BordeModel, BrasModel, CachingModel, RaiModel
from handler import TrafficHandler
from test import DatabasePostgresTest, DatabaseMongoTest, LayerTypeTest, ModelBordeTypeTest, BrasTypeTest


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
        inProm=20,
        inMax=30,
        outProm=20,
        outMax=30,
        idLayer="",
        typeLayer=""
    )


class TestHandlerMongo(unittest.TestCase):
    test_database: DatabaseMongoTest = DatabaseMongoTest()

    def insert_borde_traffic(self) -> TrafficHistoryModel:
        """Insert data example in the TrafficHistory table in the MongoDB."""
        example_interface = get_example_interface_borde()
        example_traffic = get_example_interface_traffic()
        interface = self.test_database.insert(table=LayerTypeTest.BORDE, data=example_interface.model_dump())
        example_traffic.idLayer = str(interface["_id"])
        example_traffic.typeLayer = LayerTypeTest.BORDE
        self.test_database.insert(table=LayerTypeTest.TRAFFIC_HISTORY, data=example_traffic.model_dump())
        return example_traffic

    def test_get_layer_borde(self):
        """Test get all traffic history of a borde layer by a 1 day."""
        example_traffic = self.insert_borde_traffic()
        trafficHandler = TrafficHandler()
        data = trafficHandler.get_traffic_layer_by_days_before(
            layer_type=example_traffic.typeLayer,
            day_before=1
        )
        data_columns = data.columns.to_list()
        neccesary_columns = [
            HeaderDataFrame.INTERFACE,
            HeaderDataFrame.TYPE, 
            HeaderDataFrame.CAPACITY,
            HeaderDataFrame.DATE, 
            HeaderDataFrame.TIME,
            HeaderDataFrame.IN_PROM, 
            HeaderDataFrame.OUT_PROM, 
            HeaderDataFrame.IN_MAX, 
            HeaderDataFrame.OUT_MAX
        ]
        self.test_database.clean(table=LayerTypeTest.BORDE)
        self.test_database.clean(table=LayerTypeTest.TRAFFIC_HISTORY)
        
        self.assertFalse(data.empty)
        self.assertEqual(data_columns, neccesary_columns)


class TestHandlerPostgres(unittest.TestCase):
    test_database: DatabasePostgresTest = DatabasePostgresTest()

    def create_table(self) -> None:
        """Create tables in the PostgreSQL if does not exist."""
        self.test_database.create(
            table=LayerTypeTest.BORDE,
            query=f"""
                ({BordeFieldDatabase.ID} INTEGER PRIMARY KEY,
                    {BordeFieldDatabase.NAME} VARCHAR(100) NOT NULL,
                    {BordeFieldDatabase.MODEL} VARCHAR(15) NOT NULL,
                    {BordeFieldDatabase.CAPACITY} SMALLINT NOT NULL,
                    {BordeFieldDatabase.CREATE_AT} DATE DEFAULT CURRENT_DATE,
                    CONSTRAINT type_model CHECK (
                        {BordeFieldDatabase.MODEL} IN (
                            '{ModelBordeTypeTest.CISCO}',
                            '{ModelBordeTypeTest.HUAWEI}'
                        )
                    ),
                    CONSTRAINT {LayerTypeTest.BORDE}_unique UNIQUE ({BordeFieldDatabase.NAME}, {BordeFieldDatabase.MODEL})
                )
            """
        )
        self.test_database.create(
            table=LayerTypeTest.TRAFFIC_HISTORY,
            query=f"""
                (
                    {TrafficHistoryFieldDatabase.DATE} DATE NOT NULL,
                    {TrafficHistoryFieldDatabase.TIME} TIME NOT NULL,
                    {TrafficHistoryFieldDatabase.ID_LAYER} INTEGER NOT NULL,
                    {TrafficHistoryFieldDatabase.TYPE_LAYER} VARCHAR(15) NOT NULL,
                    {TrafficHistoryFieldDatabase.IN_PROM} REAL NOT NULL,
                    {TrafficHistoryFieldDatabase.OUT_PROM} REAL NOT NULL,
                    {TrafficHistoryFieldDatabase.IN_MAX} REAL NOT NULL,
                    {TrafficHistoryFieldDatabase.OUT_MAX} REAL NOT NULL,
                    CONSTRAINT {LayerTypeTest.TRAFFIC_HISTORY}_pkey PRIMARY KEY (
                        {TrafficHistoryFieldDatabase.DATE}, 
                        {TrafficHistoryFieldDatabase.TIME}, 
                        {TrafficHistoryFieldDatabase.ID_LAYER},
                        {TrafficHistoryFieldDatabase.TYPE_LAYER}
                    )
                )
            """
        )

    def insert_borde_traffic(self) -> TrafficHistoryModel:
        """Insert data example in the borde and traffic history table in the PostgreSQL."""
        example_interface = get_example_interface_borde()
        self.create_table()
        self.test_database.insert(
            table=LayerTypeTest.BORDE, 
            query=f"""
                ({BordeFieldDatabase.ID}, 
                    {BordeFieldDatabase.NAME}, 
                    {BordeFieldDatabase.MODEL}, 
                    {BordeFieldDatabase.CAPACITY}
                ) 
                VALUES (
                    {int(example_interface.id)},
                    '{example_interface.name}',
                    '{example_interface.model}',
                    {example_interface.capacity}
                )
            """
        )
        example_traffic = get_example_interface_traffic()
        example_traffic.idLayer = example_interface.id
        example_traffic.typeLayer = LayerTypeTest.BORDE
        self.create_table()
        self.test_database.insert(
            table=LayerTypeTest.TRAFFIC_HISTORY, 
            query=f"""
                ({TrafficHistoryFieldDatabase.DATE}, 
                    {TrafficHistoryFieldDatabase.TIME}, 
                    {TrafficHistoryFieldDatabase.ID_LAYER}, 
                    {TrafficHistoryFieldDatabase.TYPE_LAYER}, 
                    {TrafficHistoryFieldDatabase.IN_PROM}, 
                    {TrafficHistoryFieldDatabase.IN_MAX}, 
                    {TrafficHistoryFieldDatabase.OUT_PROM}, 
                    {TrafficHistoryFieldDatabase.OUT_MAX}
                ) 
                VALUES (
                    '{example_traffic.date}',
                    '{example_traffic.time}',
                    {example_traffic.idLayer},
                    '{example_traffic.typeLayer}',
                    {example_traffic.inProm},
                    {example_traffic.inMax},
                    {example_traffic.outProm},
                    {example_traffic.outMax}
                )
            """
        )
        return example_traffic
    
    def test_get_layer_borde(self):
        """Test get all traffic history of a borde layer by a 1 day."""
        example_traffic = self.insert_borde_traffic()
        trafficHandler = TrafficHandler(db_backup=True)
        data = trafficHandler.get_traffic_layer_by_days_before(
            layer_type=example_traffic.typeLayer,
            day_before=1
        )
        data_columns = data.columns.to_list()
        neccesary_columns = [
            HeaderDataFrame.INTERFACE,
            HeaderDataFrame.TYPE, 
            HeaderDataFrame.CAPACITY,
            HeaderDataFrame.DATE, 
            HeaderDataFrame.TIME,
            HeaderDataFrame.IN_PROM, 
            HeaderDataFrame.OUT_PROM, 
            HeaderDataFrame.IN_MAX, 
            HeaderDataFrame.OUT_MAX
        ]
        self.test_database.clean(table=LayerTypeTest.BORDE)
        self.test_database.clean(table=LayerTypeTest.TRAFFIC_HISTORY)
        
        self.assertFalse(data.empty)
        self.assertEqual(data_columns, neccesary_columns)


if __name__ == "__main__":
    unittest.main()