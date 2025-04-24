import unittest
from database.libs.factory.postgres import PostgresDatabaseFactory
from database.libs.factory.mongo import MongoDatabaseFactory
from utils.config import ConfigurationHandler


class TestDatabase(unittest.TestCase):

    def test_connection_postgres(self) -> None:
        """Test to get connection to PostgreSQL database."""
        config = ConfigurationHandler()
        uri = config.uri_postgres
        database = PostgresDatabaseFactory().get_database(uri=uri)
        self.assertTrue(database)
        self.assertTrue(database.connected)
        database.close_connection()

    def test_connection_mongo(self) -> None:
        """Test to get connection to MongoDB database."""
        config = ConfigurationHandler()
        uri = config.uri_mongo
        database = MongoDatabaseFactory().get_database(uri=uri)
        self.assertTrue(database)
        self.assertTrue(database.connected)
        database.close_connection()


if __name__ == "__main":
    unittest.main()
