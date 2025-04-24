import os
import unittest
from dotenv import load_dotenv
from database.libs.factory.postgres import PostgresDatabaseFactory
from database.libs.product.postgres import PostgresDatabase
from database.libs.factory.mongo import MongoDatabaseFactory
from database.libs.product.mongo import MongoDatabase
from utils.config import ConfigurationHandler


load_dotenv(override=True)

URI_TEST_MONGO = os.getenv("URI_TEST_MONGO")
URI_TEST_POSTGRES = os.getenv("URI_TEST_POSTGRES")

class TestDatabase(unittest.TestCase):

    def test_connection_postgres(self) -> None:
        """Test to get connection to PostgreSQL database."""
        config = ConfigurationHandler().set_uri(uri_postgres=URI_TEST_POSTGRES)
        uri = config.uri_postgres
        database = PostgresDatabaseFactory().get_database(uri=uri)
        self.assertTrue(database)
        self.assertTrue(database.connected)
        database.close_connection()

    def test_connection_mongo(self) -> None:
        """Test to get connection to MongoDB database."""
        config = ConfigurationHandler().set_uri(uri_mongo=URI_TEST_MONGO)
        uri = config.uri_mongo
        database = MongoDatabaseFactory().get_database(uri=uri)
        self.assertTrue(database)
        self.assertTrue(database.connected)
        database.close_connection()


if __name__ == "__main":
    unittest.main()
