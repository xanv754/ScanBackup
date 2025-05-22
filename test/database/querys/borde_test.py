import unittest
import random
from datetime import datetime
from database import BordeFieldDatabase, MongoBordeQuery, PostgresBordeQuery
from model import BordeModel, BordeFieldModel
from test import DatabasePostgresTest, DatabaseMongoTest, ModelBordeTypeTest, LayerTypeTest


def get_example_interface() -> BordeModel:
    """Get example interface."""
    return BordeModel(
        id=str(random.randint(0, 1000)),
        name="interface_test_" + str(random.randint(0, 1000)),
        model=ModelBordeTypeTest.CISCO,
        capacity=0,
        createAt=datetime.now().strftime("%Y-%m-%d")
    )


class TestMongo(unittest.TestCase):
    test_database: DatabaseMongoTest = DatabaseMongoTest()

    def test_insert(self):
        """Test insert a new interface of Borde layer in the MongoDB."""
        example_interface = get_example_interface()
        database = MongoBordeQuery()
        response = database.new_interface(new=example_interface)
        self.test_database.clean(table=LayerTypeTest.BORDE)

        self.assertTrue(response)

    def test_get(self):
        """Test get an interface of Borde layer in the MongoDB."""
        example_interface = get_example_interface()
        self.test_database.insert(table=LayerTypeTest.BORDE, data=example_interface.model_dump())
        database = MongoBordeQuery()
        interface = database.get_interface(name=example_interface.name)
        self.test_database.clean(table=LayerTypeTest.BORDE)

        self.assertFalse(interface.empty)
        self.assertEqual(interface[BordeFieldModel.name].iloc[0], example_interface.name)

    def test_get_all(self):
        """Test get all interfaces of Borde layer in the MongoDB."""
        example_interface = get_example_interface()
        self.test_database.insert(table=LayerTypeTest.BORDE, data=example_interface.model_dump())
        database = MongoBordeQuery()
        interfaces = database.get_interfaces()
        self.test_database.clean(table=LayerTypeTest.BORDE)
        
        self.assertFalse(interfaces.empty)


class TestPostgres(unittest.TestCase):
    test_database: DatabasePostgresTest = DatabasePostgresTest()

    def create_table(self) -> None:
        """Create Borde table in the PostgreSQL if does not exist."""
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
            """)

    def insert(self) -> BordeModel:
        """Insert data example in the Borde table in the PostgreSQL."""
        example_interface = get_example_interface()
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
        return example_interface

    def test_insert(self):
        """Test insert a new interface of Borde layer in the PostgreSQL."""
        example_interface = get_example_interface()
        database = PostgresBordeQuery()
        response = database.new_interface(new=example_interface)
        self.test_database.clean(table=LayerTypeTest.BORDE)

        self.assertTrue(response)

    def test_get(self):
        """Test get an interface of Borde layer in the PostgreSQL."""
        example_interface = self.insert()
        database = PostgresBordeQuery()
        interface = database.get_interface(name=example_interface.name)
        self.test_database.clean(table=LayerTypeTest.BORDE)
        
        self.assertFalse(interface.empty)
        self.assertEqual(interface[BordeFieldModel.name].iloc[0], example_interface.name)

    def test_get_all(self):
        """Test get all interfaces of Borde layer in the PostgreSQL."""
        self.insert()
        database = PostgresBordeQuery()
        interfaces = database.get_interfaces()
        self.test_database.clean(table=LayerTypeTest.BORDE)
        
        self.assertFalse(interfaces.empty)


if __name__ == "__main__":
    unittest.main()