import os
import unittest
import psycopg2
from dotenv import load_dotenv
from database.postgres import PostgresDatabase
from utils.config import ConfigurationHandler


load_dotenv(override=True)


class TestDatabase(unittest.TestCase):

    def test_connection(self) -> None:
        """Test to get connection to database."""
        URI_TEST = os.getenv("URI_TEST")
        if not URI_TEST:
            self.assertTrue(False)
        else:
            database = PostgresDatabase.set_uri(URI_TEST)
            connection = database.get_connection()
            self.assertTrue(connection)


    def test_get_cursor(self) -> None:
        """Test to get cursor database."""
        URI_TEST = os.getenv("URI_TEST")
        if not URI_TEST:
            self.assertTrue(False)
        else:
            database = PostgresDatabase.set_uri(URI_TEST)
            cursor = database.get_cursor()
            self.assertTrue(cursor)


if __name__ == "__main":
    unittest.main()
