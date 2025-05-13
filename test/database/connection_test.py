import unittest
from database.libs.factory.postgres import PostgresDatabaseFactory
from database.libs.factory.mongo import MongoDatabaseFactory
from utils.config import ConfigurationHandler


class TestDatabaseMongo(unittest.TestCase):
    """Test to get connection to MongoDB database."""

    def test_connection(self) -> None:
        """Test to get connection to MongoDB database."""
        config = ConfigurationHandler()
        uri = config.uri_mongo
        factory = MongoDatabaseFactory()
        database = factory.get_database(uri=uri)
        database.open_connection()
        self.assertTrue(database)
        self.assertTrue(database.connected)
        database.close_connection()


class TestDatabasePostgres(unittest.TestCase):
    """Test to get connection to PostgreSQL database."""

    def test_connection(self) -> None:
        """Test to get connection to PostgreSQL database."""
        config = ConfigurationHandler()
        uri = config.uri_postgres
        factory = PostgresDatabaseFactory()
        database = factory.get_database(uri=uri)
        database.open_connection()
        self.assertTrue(database)
        self.assertTrue(database.connected)
        database.close_connection()
        

if __name__ == "__main":
    unittest.main()
