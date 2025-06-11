import unittest
import random
from datetime import datetime
from database import CachingFieldDatabase, MongoCachingQuery, PostgresCachingQuery
from model import CachingModel, CachingFieldModel
from test import DatabasePostgresTest, DatabaseMongoTest, LayerTypeTest


def get_example_interface() -> CachingModel:
    """Get example interface."""
    return CachingModel(
        id=str(random.randint(0, 1000)),
        name="interface_test_" + str(random.randint(0, 1000)),
        service="service_test_" + str(random.randint(0, 1000)),
        capacity=0,
        createAt=datetime.now().strftime("%Y-%m-%d")
    )


class TestMongo(unittest.TestCase):
    test_database: DatabaseMongoTest = DatabaseMongoTest()

    def test_insert(self):
        """Test insert a new interface of Caching layer in the MongoDB."""
        example_interface = get_example_interface()
        database = MongoCachingQuery(uri=self.test_database.uri)
        response = database.new_interface(new=example_interface)
        self.test_database.clean(table=LayerTypeTest.CACHING)

        self.assertTrue(response)

    def test_get(self):
        """Test get an interface of Caching layer in the MongoDB."""
        example_interface = get_example_interface()
        self.test_database.insert(table=LayerTypeTest.CACHING, data=example_interface.model_dump())
        database = MongoCachingQuery(uri=self.test_database.uri)
        interface = database.get_interface(name=example_interface.name)
        self.test_database.clean(table=LayerTypeTest.CACHING)
        
        self.assertFalse(interface.empty)
        self.assertEqual(interface[CachingFieldModel.name].iloc[0], example_interface.name)

    def test_get_all(self):
        """Test get all interfaces of Caching layer in the MongoDB."""
        example_interface = get_example_interface()
        self.test_database.insert(table=LayerTypeTest.CACHING, data=example_interface.model_dump())
        database = MongoCachingQuery(uri=self.test_database.uri)
        interfaces = database.get_interfaces()
        self.test_database.clean(table=LayerTypeTest.CACHING)
        
        self.assertIsNotNone(interfaces)


class TestPostgres(unittest.TestCase):
    test_database: DatabasePostgresTest = DatabasePostgresTest()

    def create_table(self) -> None:
        """Create Caching table in the PostgreSQL if does not exist."""
        self.test_database.create(
            table=LayerTypeTest.CACHING,
            query=f"""
                ({CachingFieldDatabase.ID} INTEGER PRIMARY KEY,
                    {CachingFieldDatabase.NAME} VARCHAR(150) NOT NULL,
                    {CachingFieldDatabase.SERVICE} VARCHAR(20) NOT NULL,
                    {CachingFieldDatabase.CAPACITY} REAL NOT NULL,
                    {CachingFieldDatabase.CREATE_AT} DATE DEFAULT CURRENT_DATE,
                    CONSTRAINT {LayerTypeTest.CACHING}_unique UNIQUE ({CachingFieldDatabase.NAME}, {CachingFieldDatabase.SERVICE})
                )
            """)

    def insert(self) -> CachingModel:
        """Insert data example in the Caching table in the PostgreSQL."""
        example_interface = get_example_interface()
        self.create_table()
        self.test_database.insert(
            table=LayerTypeTest.CACHING, 
            query=f"""
                ({CachingFieldDatabase.ID}, 
                    {CachingFieldDatabase.NAME}, 
                    {CachingFieldDatabase.SERVICE},
                    {CachingFieldDatabase.CAPACITY}
                ) 
                VALUES (
                    {int(example_interface.id)},
                    '{example_interface.name}',
                    '{example_interface.service}',
                    {example_interface.capacity}
                )
            """
        )
        return example_interface

    def test_insert(self):
        """Test insert a new interface of Caching layer in the PostgreSQL."""
        example_interface = get_example_interface()
        database = PostgresCachingQuery(uri=self.test_database.uri)
        response = database.new_interface(new=example_interface)
        self.test_database.clean(table=LayerTypeTest.CACHING)

        self.assertTrue(response)

    def test_get(self):
        """Test get an interface of Caching layer in the PostgreSQL."""
        example_interface = self.insert()
        database = PostgresCachingQuery(uri=self.test_database.uri)
        interface = database.get_interface(name=example_interface.name)
        self.test_database.clean(table=LayerTypeTest.CACHING)
        
        self.assertFalse(interface.empty)
        self.assertEqual(interface[CachingFieldModel.name].iloc[0], example_interface.name)

    def test_get_all(self):
        """Test get all interfaces of Caching layer in the PostgreSQL."""
        self.insert()
        database = PostgresCachingQuery(uri=self.test_database.uri)
        interfaces = database.get_interfaces()
        self.test_database.clean(table=LayerTypeTest.CACHING)
        
        self.assertFalse(interfaces.empty)


if __name__ == "__main__":
    unittest.main()