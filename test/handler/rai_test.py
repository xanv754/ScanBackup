import unittest
import random
from datetime import datetime
from constants.header import HeaderDataFrame
from database import RaiFieldDatabase
from model import RaiModel
from handler import RaiHandler
from test import DatabasePostgresTest, DatabaseMongoTest, LayerTypeTest


def get_example_interface() -> RaiModel:
    """Get example interface."""
    return RaiModel(
        id=str(random.randint(0, 1000)),
        name="interface_test_" + str(random.randint(0, 1000)),
        capacity=0,
        createAt=datetime.now().strftime("%Y-%m-%d")
    )


class TestHandlerMongo(unittest.TestCase):
    test_database: DatabaseMongoTest = DatabaseMongoTest()

    def test_get_all_interfaces(self):
        """Test get all interfaces of rai layer converted in a dataframe."""
        example_interface = get_example_interface()
        self.test_database.insert(table=LayerTypeTest.RAI, data=example_interface.model_dump())
        raiHandler = RaiHandler()
        data = raiHandler.get_all_interfaces()
        data_columns = data.columns.to_list()
        neccesary_columns = [
            HeaderDataFrame.ID,
            HeaderDataFrame.NAME,
            HeaderDataFrame.CAPACITY
        ]
        self.test_database.clean(table=LayerTypeTest.RAI)

        self.assertFalse(data.empty)
        self.assertEqual(data_columns, neccesary_columns)


class TestHandlerPostgres(unittest.TestCase):
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

    def test_get_all(self):
        """Test get all interfaces of rai layer converted in a dataframe."""
        self.insert()
        bordeHandler = RaiHandler(db_backup=True)
        data = bordeHandler.get_all_interfaces()
        data_columns = data.columns.to_list()
        neccesary_columns = [
            HeaderDataFrame.ID,
            HeaderDataFrame.NAME,
            HeaderDataFrame.CAPACITY
        ]
        self.test_database.clean(table=LayerTypeTest.RAI)

        self.assertFalse(data.empty)
        self.assertEqual(data_columns, neccesary_columns)

if __name__ == "__main__":
    unittest.main()