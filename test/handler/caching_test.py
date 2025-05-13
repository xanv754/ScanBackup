import unittest
import random
from datetime import datetime
from constants import HeaderDataFrame
from database import CachingFieldDatabase
from model import CachingModel
from handler import CachingHandler
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


class TestMongoCachingHandler(unittest.TestCase):
    test_database: DatabaseMongoTest = DatabaseMongoTest()

    def test_get_all_interfaces(self):
        """Test get all interfaces of caching layer converted in a dataframe."""
        example_interface = get_example_interface()
        self.test_database.insert(table=LayerTypeTest.CACHING, data=example_interface.model_dump())
        cachingHandler = CachingHandler()
        data = cachingHandler.get_all_interfaces()
        data_columns = data.columns.to_list()
        neccesary_columns = [
            HeaderDataFrame.ID,
            HeaderDataFrame.NAME,
            HeaderDataFrame.SERVICE,
            HeaderDataFrame.CAPACITY
        ]
        self.test_database.clean(table=LayerTypeTest.CACHING)

        self.assertFalse(data.empty)
        self.assertEqual(data_columns, neccesary_columns)


class TestHandlerPostgres(unittest.TestCase):
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
    
    def test_get_all(self):
        """Test get all interfaces of caching layer converted in a dataframe."""
        self.insert()
        bordeHandler = CachingHandler(db_backup=True)
        data = bordeHandler.get_all_interfaces()
        data_columns = data.columns.to_list()
        neccesary_columns = [
            HeaderDataFrame.ID,
            HeaderDataFrame.NAME,
            HeaderDataFrame.SERVICE,
            HeaderDataFrame.CAPACITY
        ]
        self.test_database.clean(table=LayerTypeTest.CACHING)

        self.assertFalse(data.empty)
        self.assertEqual(data_columns, neccesary_columns)


if __name__ == "__main__":
    unittest.main()