import unittest
import random
from datetime import datetime
from constants.header import HeaderDataFrame
from database import BordeFieldDatabase
from model import BordeModel
from handler import BordeHandler
from test import DatabaseMongoTest, DatabasePostgresTest, ModelBordeTypeTest, LayerTypeTest


def get_example_interface() -> BordeModel:
    """Get example interface of borde layer."""
    return BordeModel(
        id=str(random.randint(0, 1000)),
        name="interface_test_" + str(random.randint(0, 1000)),
        model=ModelBordeTypeTest.CISCO,
        capacity=10,
        createAt=datetime.now().strftime("%Y-%m-%d")
    )


class TestHandlerMongo(unittest.TestCase):
    test_database: DatabaseMongoTest = DatabaseMongoTest()

    def test_get_all(self):
        """Test get all interfaces of borde layer converted in a dataframe."""
        example_interface = get_example_interface()
        self.test_database.insert(table=LayerTypeTest.BORDE, data=example_interface.model_dump())
        bordeHandler = BordeHandler(uri=self.test_database.uri)
        data = bordeHandler.get_all_interfaces()
        data_columns = data.columns.to_list()
        neccesary_columns = [
            HeaderDataFrame.ID,
            HeaderDataFrame.NAME,
            HeaderDataFrame.MODEL,
            HeaderDataFrame.CAPACITY
        ]
        self.test_database.clean(table=LayerTypeTest.BORDE)

        self.assertFalse(data.empty)
        self.assertEqual(data_columns, neccesary_columns)


class TestHandlerPostgres(unittest.TestCase):
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
            """
        )

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
    
    def test_get_all(self):
        """Test get all interfaces of borde layer converted in a dataframe."""
        self.insert()
        bordeHandler = BordeHandler(db_backup=True, uri=self.test_database.uri)
        data = bordeHandler.get_all_interfaces()
        data_columns = data.columns.to_list()
        neccesary_columns = [
            HeaderDataFrame.ID,
            HeaderDataFrame.NAME,
            HeaderDataFrame.MODEL,
            HeaderDataFrame.CAPACITY
        ]
        self.test_database.clean(table=LayerTypeTest.BORDE)

        self.assertFalse(data.empty)
        self.assertEqual(data_columns, neccesary_columns)


if __name__ == "__main__":
    unittest.main()