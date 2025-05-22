import unittest
import random
from datetime import datetime
from database import BrasFieldDatabase, MongoBrasQuery, PostgresBrasQuery
from model import BrasModel, BrasFieldModel
from test import DatabasePostgresTest, DatabaseMongoTest, LayerTypeTest, BrasTypeTest


def get_example_interface() -> BrasModel:
    """Get example interface."""
    return BrasModel(
        id=str(random.randint(0, 1000)),
        name="interface_test_" + str(random.randint(0, 1000)),
        capacity=0,
        type=BrasTypeTest.UPLINK,
        createAt=datetime.now().strftime("%Y-%m-%d")
    )


class TestMongo(unittest.TestCase):
    test_database: DatabaseMongoTest = DatabaseMongoTest()

    def test_insert(self):
        """Test insert a new interface of Bras layer in the MongoDB."""
        example_interface = get_example_interface()
        database = MongoBrasQuery()
        response = database.new_interface(new=example_interface)
        self.test_database.clean(table=LayerTypeTest.BRAS)

        self.assertTrue(response)

    def test_get(self):
        """Test get an interface of Bras layer in the MongoDB."""
        example_interface = get_example_interface()
        self.test_database.insert(table=LayerTypeTest.BRAS, data=example_interface.model_dump())
        database = MongoBrasQuery()
        interface = database.get_interface(brasname=example_interface.name, type=example_interface.type)
        self.test_database.clean(table=LayerTypeTest.BRAS)

        self.assertFalse(interface.empty)
        self.assertEqual(interface[BrasFieldModel.name].iloc[0], example_interface.name)

    def test_get_all(self):
        """Test get all interfaces of Bras layer in the MongoDB."""
        example_interface = get_example_interface()
        self.test_database.insert(table=LayerTypeTest.BRAS, data=example_interface.model_dump())
        database = MongoBrasQuery()
        interfaces = database.get_interfaces()
        self.test_database.clean(table=LayerTypeTest.BRAS)
        
        self.assertFalse(interfaces.empty)


class TestPostgres(unittest.TestCase):
    test_database: DatabasePostgresTest = DatabasePostgresTest()

    def create_table(self) -> None:
        """Create Bras table in the PostgreSQL if does not exist."""
        self.test_database.create(
            table=LayerTypeTest.BRAS,
            query=f"""
                ({BrasFieldDatabase.ID} INTEGER PRIMARY KEY,
                    {BrasFieldDatabase.NAME} VARCHAR(100) NOT NULL,
                    {BrasFieldDatabase.TYPE} VARCHAR(15) NOT NULL,
                    {BrasFieldDatabase.CAPACITY} SMALLINT NOT NULL,
                    {BrasFieldDatabase.CREATE_AT} DATE DEFAULT CURRENT_DATE,
                    CONSTRAINT type_bras CHECK (
                        {BrasFieldDatabase.TYPE} IN (
                            '{BrasTypeTest.UPLINK}',
                            '{BrasTypeTest.DOWNLINK}'
                        )
                    ),
                    CONSTRAINT {LayerTypeTest.BRAS}_unique UNIQUE ({BrasFieldDatabase.NAME}, {BrasFieldDatabase.TYPE})
                )
            """)

    def insert(self) -> BrasModel:
        """Insert data example in the Bras table in the PostgreSQL."""
        example_interface = get_example_interface()
        self.create_table()
        self.test_database.insert(
            table=LayerTypeTest.BRAS, 
            query=f"""
                ({BrasFieldDatabase.ID}, 
                    {BrasFieldDatabase.NAME}, 
                    {BrasFieldDatabase.TYPE},
                    {BrasFieldDatabase.CAPACITY}
                ) 
                VALUES (
                    {int(example_interface.id)},
                    '{example_interface.name}',
                    '{example_interface.type}',
                    {example_interface.capacity}
                )
            """
        )
        return example_interface

    def test_insert(self):
        """Test insert a new interface of Bras layer in the PostgreSQL."""
        example_interface = get_example_interface()
        database = PostgresBrasQuery()
        response = database.new_interface(new=example_interface)
        self.test_database.clean(table=LayerTypeTest.BRAS)

        self.assertTrue(response)

    def test_get(self):
        """Test get an interface of Bras layer in the PostgreSQL."""
        example_interface = self.insert()
        database = PostgresBrasQuery()
        interface = database.get_interface(brasname=example_interface.name, type=example_interface.type)
        self.test_database.clean(table=LayerTypeTest.BRAS)
        
        self.assertFalse(interface.empty)
        self.assertEqual(interface[BrasFieldModel.name].iloc[0], example_interface.name)

    def test_get_all(self):
        """Test get all interfaces of Bras layer in the PostgreSQL."""
        self.insert()
        database = PostgresBrasQuery()
        interfaces = database.get_interfaces()
        self.test_database.clean(table=LayerTypeTest.BRAS)
        
        self.assertFalse(interfaces.empty)


if __name__ == "__main__":
    unittest.main()