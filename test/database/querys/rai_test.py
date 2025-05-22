import unittest
import random
from datetime import datetime
from database import RaiFieldDatabase, MongoRaiQuery, PostgresRaiQuery
from model import RaiModel, RaiFieldModel
from test import DatabasePostgresTest, DatabaseMongoTest, LayerTypeTest


def get_example_interface() -> RaiModel:
    """Get example interface."""
    return RaiModel(
        id=str(random.randint(0, 1000)),
        name="interface_test_" + str(random.randint(0, 1000)),
        capacity=0,
        createAt=datetime.now().strftime("%Y-%m-%d")
    )


class TestMongo(unittest.TestCase):
    test_database: DatabaseMongoTest = DatabaseMongoTest()

    def test_insert(self):
        """Test insert a new interface of Rai layer in the MongoDB."""
        example_interface = get_example_interface()
        database = MongoRaiQuery() 
        response = database.new_interface(new=example_interface)
        self.test_database.clean(table=LayerTypeTest.RAI)

        self.assertTrue(response)

    def test_get(self):
        """Test get an interface of Rai layer in the MongoDB."""
        example_interface = get_example_interface()
        self.test_database.insert(table=LayerTypeTest.RAI, data=example_interface.model_dump())
        database = MongoRaiQuery()
        interface = database.get_interface(name=example_interface.name)
        self.test_database.clean(table=LayerTypeTest.RAI)
        
        self.assertFalse(interface.empty)
        self.assertEqual(interface[RaiFieldModel.name].iloc[0], example_interface.name)

    def test_get_all(self):
        """Test get all interfaces of Rai layer in the MongoDB."""
        example_interface = get_example_interface()
        self.test_database.insert(table=LayerTypeTest.RAI, data=example_interface.model_dump())
        database = MongoRaiQuery()
        interfaces = database.get_interfaces()
        self.test_database.clean(table=LayerTypeTest.RAI)
        
        self.assertFalse(interfaces.empty)


class TestPostgres(unittest.TestCase):
    test_database: DatabasePostgresTest = DatabasePostgresTest()

    def create_table(self) -> None:
        """Create Rai table in the PostgreSQL if does not exist."""
        self.test_database.create(
            table=LayerTypeTest.RAI,
            query=f"""
                ({RaiFieldDatabase.ID} INTEGER PRIMARY KEY,
                    {RaiFieldDatabase.NAME} VARCHAR(150) NOT NULL,
                    {RaiFieldDatabase.CAPACITY} REAL NOT NULL,
                    {RaiFieldDatabase.CREATE_AT} DATE DEFAULT CURRENT_DATE,
                    CONSTRAINT {LayerTypeTest.RAI}_unique UNIQUE ({RaiFieldDatabase.NAME})
                )
            """)

    def insert(self) -> RaiModel:
        """Insert data example in the Rai table in the PostgreSQL."""
        example_interface = get_example_interface()
        self.create_table()
        self.test_database.insert(
            table=LayerTypeTest.RAI, 
            query=f"""
                ({RaiFieldDatabase.ID}, 
                    {RaiFieldDatabase.NAME}, 
                    {RaiFieldDatabase.CAPACITY}
                ) 
                VALUES (
                    {int(example_interface.id)},
                    '{example_interface.name}',
                    {example_interface.capacity}
                )
            """
        )
        return example_interface

    def test_insert(self):
        """Test insert a new interface of Rai layer in the PostgreSQL."""
        example_interface = get_example_interface()
        database = PostgresRaiQuery()
        response = database.new_interface(new=example_interface)
        self.test_database.clean(table=LayerTypeTest.RAI)

        self.assertTrue(response)

    def test_get(self):
        """Test get an interface of Rai layer in the PostgreSQL."""
        example_interface = self.insert()
        database = PostgresRaiQuery()
        interface = database.get_interface(name=example_interface.name)
        self.test_database.clean(table=LayerTypeTest.RAI)
        
        self.assertFalse(interface.empty)
        self.assertEqual(interface[RaiFieldModel.name].iloc[0], example_interface.name)

    def test_get_all(self):
        """Test get all interfaces of Rai layer in the PostgreSQL."""
        self.insert()
        database = PostgresRaiQuery()
        interfaces = database.get_interfaces()
        self.test_database.clean(table=LayerTypeTest.RAI)
        
        self.assertFalse(interfaces.empty)


if __name__ == "__main__":
    unittest.main()