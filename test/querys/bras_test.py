import unittest
from database import BrasMongoQuery, PostgresBrasQuery
from model import BrasFieldModel
from test import DatabaseBrasTest


class Query(unittest.TestCase):
    mongo_db_test: DatabaseBrasTest = DatabaseBrasTest()
    postgres_db_test: DatabaseBrasTest = DatabaseBrasTest(db_backup=True)

    def test_insert(self):
        """Test insert a new interface of Bras layer in the database."""
        example_interface = self.mongo_db_test.get_exampĺe()
        database = BrasMongoQuery(uri=self.mongo_db_test.uri)
        response = database.new_interface(new=example_interface)
        self.mongo_db_test.clean()
        self.assertTrue(response)

        example_interface = self.postgres_db_test.get_exampĺe()
        database = PostgresBrasQuery(uri=self.postgres_db_test.uri)
        response = database.new_interface(new=example_interface)
        self.postgres_db_test.clean()
        self.assertTrue(response)

    def test_get(self):
        """Test get an interface of Bras layer in the database."""
        example_interface = self.mongo_db_test.insert()
        database = BrasMongoQuery(uri=self.mongo_db_test.uri)
        interface = database.get_interface(brasname=example_interface.name, type=example_interface.type)
        print(interface)
        self.mongo_db_test.clean()
        self.assertFalse(interface.empty)
        self.assertEqual(interface[BrasFieldModel.name].iloc[0], example_interface.name)

        example_interface = self.postgres_db_test.insert()
        database = PostgresBrasQuery(uri=self.postgres_db_test.uri)
        interface = database.get_interface(brasname=example_interface.name, type=example_interface.type)
        print(interface)
        self.postgres_db_test.clean()
        self.assertFalse(interface.empty)
        self.assertEqual(interface[BrasFieldModel.name].iloc[0], example_interface.name)

    def test_get_all(self):
        """Test get all interfaces of Bras layer in the database."""
        self.mongo_db_test.insert()
        database = BrasMongoQuery(uri=self.mongo_db_test.uri)
        interfaces = database.get_interfaces()
        print(interfaces)
        self.mongo_db_test.clean()
        self.assertFalse(interfaces.empty)

        self.postgres_db_test.insert()
        database = PostgresBrasQuery(uri=self.postgres_db_test.uri)
        interfaces = database.get_interfaces()
        print(interfaces)
        self.postgres_db_test.clean()
        self.assertFalse(interfaces.empty)


if __name__ == "__main__":
    unittest.main()