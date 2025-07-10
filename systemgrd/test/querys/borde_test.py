import unittest
from systemgrd.database import BordeMongoQuery
from systemgrd.test import DatabaseBorderTest, BBIPFieldName


class Query(unittest.TestCase):
    mongo_db_test: DatabaseBorderTest = DatabaseBorderTest()

    def test_insert(self):
        """Test insert a new interface of Borde layer in the database."""
        example_interface = self.mongo_db_test.get_exampĺe()
        database = BordeMongoQuery(uri=self.mongo_db_test.uri)
        response = database.new_interface(data=[example_interface])
        self.mongo_db_test.clean()
        self.assertTrue(response)

    def test_get(self):
        """Test get an interface of Borde layer in the database."""
        example_interface = self.mongo_db_test.insert()
        database = BordeMongoQuery(uri=self.mongo_db_test.uri)
        interface = database.get_interface(name=example_interface.name)
        print(interface)
        self.mongo_db_test.clean()
        self.assertFalse(interface.empty)
        self.assertEqual(interface[BBIPFieldName.NAME].iloc[0], example_interface.name)

    def test_get_all(self):
        """Test get all interfaces of Borde layer in the database."""
        self.mongo_db_test.insert()
        database = BordeMongoQuery(uri=self.mongo_db_test.uri)
        interfaces = database.get_interfaces()
        print(interfaces)
        self.mongo_db_test.clean()
        self.assertFalse(interfaces.empty)

if __name__ == "__main__":
    unittest.main()