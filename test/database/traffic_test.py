import random
import unittest
from datetime import datetime
from model.trafficHistory import TrafficHistoryModel
from database.querys.traffic.mongo import MongoTrafficHistoryQuery
from database.querys.traffic.postgres import PostgresTrafficHistoryQuery
from test import DatabasePostgresTest, DatabaseMongoTest, LayerTypeTest, TrafficFieldDatabaseTest

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

    def test_insert_traffic(self):
        """Test insert a new traffic of a layer in the MongoDB."""
        database = MongoTrafficHistoryQuery()
        new_traffic = get_example_traffic()
        response = database.new_traffic(traffic=[new_traffic])
        self.test_database.clean(table=LayerTypeTest.TRAFFIC_HISTORY)

        self.assertTrue(response)

    def test_get_traffic(self):
        """Test get a traffic of a layer in the MongoDB."""
        example_traffic = get_example_traffic()
        self.test_database.insert(table=LayerTypeTest.TRAFFIC_HISTORY, data=example_traffic.model_dump())
        database = MongoTrafficHistoryQuery()
        response = database.get_traffic(
            date=example_traffic.date, 
            time=example_traffic.time, 
            id_layer=example_traffic.idLayer
        )
        self.test_database.clean(table=LayerTypeTest.TRAFFIC_HISTORY)

        self.assertIsNotNone(response)
        self.assertEqual(response.date, example_traffic.date)
        self.assertEqual(response.time, example_traffic.time)
        self.assertEqual(response.idLayer, example_traffic.idLayer)

    def test_get_traffic_interface_by_date(self):
        """Test get all traffic history of a interface by date in MongoDB."""
        example_traffic = get_example_traffic()
        self.test_database.insert(table=LayerTypeTest.TRAFFIC_HISTORY, data=example_traffic.model_dump())
        database = MongoTrafficHistoryQuery()
        interface = database.get_traffic_interface_by_date(
            id=example_traffic.idLayer, 
            date=example_traffic.date
        )
        self.test_database.clean(table=LayerTypeTest.TRAFFIC_HISTORY)

        self.assertIsNotNone(interface)
        self.assertEqual(interface[0].date, example_traffic.date)
        self.assertEqual(interface[0].idLayer, example_traffic.idLayer)

    def test_get_traffic_layer_by_date(self):
        """Test get all traffic history of a type layer by date in MongoDB."""
        example_traffic = get_example_traffic()
        self.test_database.insert(table=LayerTypeTest.TRAFFIC_HISTORY, data=example_traffic.model_dump())
        database = MongoTrafficHistoryQuery()
        interface = database.get_traffic_layer_by_date(
            layer_type=example_traffic.typeLayer, 
            date=example_traffic.date
        )
        self.test_database.clean(table=LayerTypeTest.TRAFFIC_HISTORY)

        self.assertIsNotNone(interface)
        self.assertEqual(interface[0].date, example_traffic.date)
        self.assertEqual(interface[0].typeLayer, example_traffic.typeLayer)

class TestPostgres(unittest.TestCase):
    test_database: DatabasePostgresTest = DatabasePostgresTest()

    def create_table(self) -> None:
        """Create TrafficHistory table in the PostgreSQL if does not exist."""
        self.test_database.create(
            table=LayerTypeTest.TRAFFIC_HISTORY,
            query=f"""(
                {TrafficFieldDatabaseTest.DATE} DATE NOT NULL,
                {TrafficFieldDatabaseTest.TIME} TIME NOT NULL,
                {TrafficFieldDatabaseTest.ID_LAYER} INTEGER NOT NULL,
                {TrafficFieldDatabaseTest.TYPE_LAYER} VARCHAR(15) NOT NULL,
                {TrafficFieldDatabaseTest.IN_PROM} REAL NOT NULL,
                {TrafficFieldDatabaseTest.OUT_PROM} REAL NOT NULL,
                {TrafficFieldDatabaseTest.IN_MAX} REAL NOT NULL,
                {TrafficFieldDatabaseTest.OUT_MAX} REAL NOT NULL,
                CONSTRAINT {LayerTypeTest.TRAFFIC_HISTORY}_pkey PRIMARY KEY (
                    {TrafficFieldDatabaseTest.DATE}, 
                    {TrafficFieldDatabaseTest.TIME}, 
                    {TrafficFieldDatabaseTest.ID_LAYER},
                    {TrafficFieldDatabaseTest.TYPE_LAYER}
                )
            )
        """)

    def insert(self) -> None:
        """Insert data example in the TrafficHistory table in the PostgreSQL."""
        example_traffic = get_example_traffic()
        self.create_table()
        self.test_database.insert(
            table=LayerTypeTest.TRAFFIC_HISTORY, 
            query=f"""
                ({TrafficFieldDatabaseTest.DATE}, 
                    {TrafficFieldDatabaseTest.TIME}, 
                    {TrafficFieldDatabaseTest.ID_LAYER}, 
                    {TrafficFieldDatabaseTest.TYPE_LAYER}, 
                    {TrafficFieldDatabaseTest.IN_PROM}, 
                    {TrafficFieldDatabaseTest.IN_MAX}, 
                    {TrafficFieldDatabaseTest.OUT_PROM}, 
                    {TrafficFieldDatabaseTest.OUT_MAX}
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

    def insert_traffic(self):
        """Test insert a new traffic of a layer in the PostgreSQL."""
        pass

    def get_traffic(self):
        """Test get a traffic of a layer in the PostgreSQL."""
        pass

    def test_get_traffic_interface_by_date(self):
        """Test get all traffic history of a interface by date in the PostgreSQL."""
        example_traffic = self.insert()
        database = PostgresTrafficHistoryQuery()
        interface = database.get_traffic_interface_by_date(
            id=example_traffic.idLayer, 
            date=example_traffic.date
        )
        self.test_database.clean(table=LayerTypeTest.TRAFFIC_HISTORY)

        self.assertIsNotNone(interface)
        self.assertEqual(interface[0].date, example_traffic.date)
        self.assertEqual(interface[0].idLayer, example_traffic.idLayer)

    def test_get_traffic_layer_by_date(self):
        """Test get all traffic history of a type layer by date in PostgreSQL."""
        example_traffic = self.insert()
        database = PostgresTrafficHistoryQuery()
        interface = database.get_traffic_layer_by_date(
            layer_type=example_traffic.typeLayer, 
            date=example_traffic.date
        )
        self.test_database.clean(table=LayerTypeTest.TRAFFIC_HISTORY)
        
        self.assertIsNotNone(interface)
        self.assertEqual(interface[0].date, example_traffic.date)
        self.assertEqual(interface[0].typeLayer, example_traffic.typeLayer)


if __name__ == "__main__":
    unittest.main()