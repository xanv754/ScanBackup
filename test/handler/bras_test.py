import unittest
import random
from datetime import datetime
from constants import HeaderDataFrame
from database import BrasFieldDatabase
from model import BrasModel
from handler import BrasHandler
from test import DatabasePostgresTest, DatabaseMongoTest, LayerTypeTest, BrasTypeTest


def get_example_interface() -> BrasModel:
    """Get example interface."""
    return BrasModel(
        id=str(random.randint(0, 1000)),
        name="interface_test_" + str(random.randint(0, 1000)),
        type=BrasTypeTest.UPLINK,
        capacity=0,
        createAt=datetime.now().strftime("%Y-%m-%d")
    )


class TestHandlerMongo(unittest.TestCase):
    test_database: DatabaseMongoTest = DatabaseMongoTest()

    def test_get_all_interfaces(self):
        """Test get all interfaces of bras layer converted in a dataframe."""
        example_interface = get_example_interface()
        self.test_database.insert(table=LayerTypeTest.BRAS, data=example_interface.model_dump())
        brasHandler = BrasHandler()
        data = brasHandler.get_all_interfaces()
        data_columns = data.columns.to_list()
        neccesary_columns = [
            HeaderDataFrame.ID,
            HeaderDataFrame.NAME,
            HeaderDataFrame.TYPE,
            HeaderDataFrame.CAPACITY
        ]
        self.test_database.clean(table=LayerTypeTest.BRAS)

        self.assertFalse(data.empty)
        self.assertEqual(data_columns, neccesary_columns)


class TestHandlerPostgres(unittest.TestCase):
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
    
    def test_get_all(self):
        """Test get all interfaces of bras layer converted in a dataframe."""
        self.insert()
        bordeHandler = BrasHandler(db_backup=True)
        data = bordeHandler.get_all_interfaces()
        data_columns = data.columns.to_list()
        neccesary_columns = [
            HeaderDataFrame.ID,
            HeaderDataFrame.NAME,
            HeaderDataFrame.TYPE,
            HeaderDataFrame.CAPACITY
        ]
        self.test_database.clean(table=LayerTypeTest.BRAS)

        self.assertFalse(data.empty)
        self.assertEqual(data_columns, neccesary_columns)


if __name__ == "__main__":
    unittest.main()