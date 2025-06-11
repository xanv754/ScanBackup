import random
import unittest
from datetime import datetime
from database import TrafficHistoryFieldDatabase, MongoTrafficHistoryQuery, PostgresTrafficHistoryQuery
from model import TrafficHistoryModel, TrafficHistoryFieldModel
from test import DatabasePostgresTest, DatabaseMongoTest, LayerTypeTest

def get_example_traffic() -> TrafficHistoryModel:
    """Get example traffic."""
    return TrafficHistoryModel(
        date=datetime.now().strftime("%Y-%m-%d"),
        time="00:00:00",
        inProm=0,
        inMax=0,
        outProm=0,
        outMax=0,
        idLayer=str(random.randint(0, 1000)),
        typeLayer=LayerTypeTest.BORDE
    )

class TestMongo(unittest.TestCase):
    test_database: DatabaseMongoTest = DatabaseMongoTest()

    def test_insert(self):
        """Test insert a new traffic of a layer in the MongoDB."""
        new_traffic = get_example_traffic()
        database = MongoTrafficHistoryQuery(uri=self.test_database.uri)
        response = database.new_traffic(traffic=[new_traffic])
        self.test_database.clean(table=LayerTypeTest.TRAFFIC_HISTORY)

        self.assertTrue(response)

    def test_get(self):
        """Test get a traffic of a layer in the MongoDB."""
        example_traffic = get_example_traffic()
        self.test_database.insert(table=LayerTypeTest.TRAFFIC_HISTORY, data=example_traffic.model_dump())
        database = MongoTrafficHistoryQuery(uri=self.test_database.uri)
        response = database.get_traffic(
            date=example_traffic.date, 
            time=example_traffic.time, 
            id_layer=example_traffic.idLayer
        )
        self.test_database.clean(table=LayerTypeTest.TRAFFIC_HISTORY)

        self.assertFalse(response.empty)
        self.assertEqual(response[TrafficHistoryFieldModel.date].iloc[0], example_traffic.date)
        self.assertEqual(response[TrafficHistoryFieldModel.time].iloc[0], example_traffic.time)
        self.assertEqual(str(response[TrafficHistoryFieldModel.idLayer].iloc[0]), example_traffic.idLayer)

    def test_get_by_layer_and_date(self):
        """Test get all traffic history of a type layer by date in MongoDB."""
        example_traffic = get_example_traffic()
        self.test_database.insert(table=LayerTypeTest.TRAFFIC_HISTORY, data=example_traffic.model_dump())
        database = MongoTrafficHistoryQuery(uri=self.test_database.uri)
        interface = database.get_traffic_layer_by_date(
            layer_type=example_traffic.typeLayer, 
            date=example_traffic.date
        )
        self.test_database.clean(table=LayerTypeTest.TRAFFIC_HISTORY)

        self.assertFalse(interface.empty)
        self.assertEqual(interface[TrafficHistoryFieldModel.date].iloc[0], example_traffic.date)
        self.assertEqual(interface[TrafficHistoryFieldModel.typeLayer].iloc[0], example_traffic.typeLayer)

class TestPostgres(unittest.TestCase):
    test_database: DatabasePostgresTest = DatabasePostgresTest()

    def create_table(self) -> None:
        """Create TrafficHistory table in the PostgreSQL if does not exist."""
        self.test_database.create(
            table=LayerTypeTest.TRAFFIC_HISTORY,
            query=f"""(
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
        """)

    def insert(self) -> TrafficHistoryModel:
        """Insert data example in the TrafficHistory table in the PostgreSQL."""
        example_traffic = get_example_traffic()
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

    def test_insert(self):
        """Test insert a new traffic of a layer in the PostgreSQL."""
        example_traffic = get_example_traffic()
        database = PostgresTrafficHistoryQuery(uri=self.test_database.uri)
        response = database.new_traffic(traffic=[example_traffic])
        self.test_database.clean(table=LayerTypeTest.TRAFFIC_HISTORY)

        self.assertTrue(response)

    def test_get(self):
        """Test get a traffic of a layer in the PostgreSQL."""
        example_traffic = self.insert()
        database = PostgresTrafficHistoryQuery(uri=self.test_database.uri)
        response = database.get_traffic(
            date=example_traffic.date, 
            time=example_traffic.time, 
            id_layer=example_traffic.idLayer
        )
        self.test_database.clean(table=LayerTypeTest.TRAFFIC_HISTORY)

        self.assertFalse(response.empty)
        self.assertEqual(response[TrafficHistoryFieldModel.date].iloc[0], example_traffic.date)
        self.assertEqual(response[TrafficHistoryFieldModel.time].iloc[0], example_traffic.time)
        self.assertEqual(str(response[TrafficHistoryFieldModel.idLayer].iloc[0]), example_traffic.idLayer)

    def test_get_by_layer_and_date(self):
        """Test get all traffic history of a type layer by date in PostgreSQL."""
        example_traffic = self.insert()
        database = PostgresTrafficHistoryQuery(uri=self.test_database.uri)
        interface = database.get_traffic_layer_by_date(
            layer_type=example_traffic.typeLayer, 
            date=example_traffic.date
        )
        self.test_database.clean(table=LayerTypeTest.TRAFFIC_HISTORY)
        
        self.assertFalse(interface.empty)
        self.assertEqual(interface[TrafficHistoryFieldModel.date].iloc[0], example_traffic.date)
        self.assertEqual(interface[TrafficHistoryFieldModel.typeLayer].iloc[0], example_traffic.typeLayer)


if __name__ == "__main__":
    unittest.main()