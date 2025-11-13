import unittest
from systemgrd.database import CachingMongoQuery
from systemgrd.test import DatabaseCachingTest, BBIPFieldName


class Query(unittest.TestCase):
    mongo_db_test: DatabaseCachingTest = DatabaseCachingTest()

    def test_insert(self):
        """Test insert a new interface of Caching layer in the database."""
        example_interface = self.mongo_db_test.get_exampĺe()
        database = CachingMongoQuery(uri=self.mongo_db_test.uri)
        response = database.new_interface(data=[example_interface])
        self.mongo_db_test.clean()
        self.assertTrue(response)

    def test_get(self):
        """Test get an interface of Caching layer in the database."""
        example_interface = self.mongo_db_test.insert()
        database = CachingMongoQuery(uri=self.mongo_db_test.uri)
        interface = database.get_interface(name=example_interface.name)
        print(interface)
        self.mongo_db_test.clean()
        self.assertFalse(interface.empty)
        self.assertEqual(interface[BBIPFieldName.NAME].iloc[0], example_interface.name)

    def test_get_all(self):
        """Test get all interfaces of Caching layer in the database."""
        self.mongo_db_test.insert()
        database = CachingMongoQuery(uri=self.mongo_db_test.uri)
        interfaces = database.get_interfaces()
        print(interfaces)
        self.mongo_db_test.clean()
        self.assertFalse(interfaces.empty)


if __name__ == "__main__":
    unittest.main()
