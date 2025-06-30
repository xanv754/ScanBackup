import unittest
from database import RaiMongoQuery, PostgresRaiQuery
from model import RaiFieldModel
from test import DatabaseRaiTest


class Query(unittest.TestCase):
    mongo_db_test: DatabaseRaiTest = DatabaseRaiTest()
    postgres_db_test: DatabaseRaiTest = DatabaseRaiTest(db_backup=True)

    def test_insert(self):
        """Test insert a new interface of Rai layer in the database."""
        example_interface = self.mongo_db_test.get_exampĺe()
        database = RaiMongoQuery(uri=self.mongo_db_test.uri)
        response = database.new_interface(data=example_interface)
        self.mongo_db_test.clean()
        self.assertTrue(response)

        example_interface = self.postgres_db_test.get_exampĺe()
        database = PostgresRaiQuery(uri=self.postgres_db_test.uri)
        response = database.new_interface(new=example_interface)
        self.postgres_db_test.clean()
        self.assertTrue(response)

    def test_get(self):
        """Test get an interface of Rai layer in the database."""
        example_interface = self.mongo_db_test.insert()
        database = RaiMongoQuery(uri=self.mongo_db_test.uri)
        interface = database.get_interface(name=example_interface.name)
        print(interface)
        self.mongo_db_test.clean()
        self.assertFalse(interface.empty)
        self.assertEqual(interface[RaiFieldModel.name].iloc[0], example_interface.name)

        example_interface = self.postgres_db_test.insert()
        database = PostgresRaiQuery(uri=self.postgres_db_test.uri)
        interface = database.get_interface(name=example_interface.name)
        print(interface)
        self.postgres_db_test.clean()
        self.assertFalse(interface.empty)
        self.assertEqual(interface[RaiFieldModel.name].iloc[0], example_interface.name)

    def test_get_all(self):
        """Test get all interfaces of Rai layer in the database."""
        self.mongo_db_test.insert()
        database = RaiMongoQuery(uri=self.mongo_db_test.uri)
        interfaces = database.get_interfaces()
        print(interfaces)
        self.mongo_db_test.clean()
        self.assertFalse(interfaces.empty)

        self.postgres_db_test.insert()
        database = PostgresRaiQuery(uri=self.postgres_db_test.uri)
        interfaces = database.get_interfaces()
        print(interfaces)
        self.postgres_db_test.clean()
        self.assertFalse(interfaces.empty)


if __name__ == "__main__":
    unittest.main()