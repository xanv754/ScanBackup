import unittest
from systemgrd.database import BrasMongoQuery
from systemgrd.test import DatabaseBrasTest, BBIPFieldName


class Query(unittest.TestCase):
    mongo_db_test: DatabaseBrasTest = DatabaseBrasTest()

    def test_insert(self):
        """Test insert a new interface of Bras layer in the database."""
        example_interface = self.mongo_db_test.get_exampĺe()
        database = BrasMongoQuery(uri=self.mongo_db_test.uri)
        response = database.new_interface(data=[example_interface])
        self.mongo_db_test.clean()
        self.assertTrue(response)

    def test_get(self):
        """Test get an interface of Bras layer in the database."""
        example_interface = self.mongo_db_test.insert()
        database = BrasMongoQuery(uri=self.mongo_db_test.uri)
        interface = database.get_interface(brasname=example_interface.name, type=example_interface.type)
        print(interface)
        self.mongo_db_test.clean()
        self.assertFalse(interface.empty)
        self.assertEqual(interface[BBIPFieldName.NAME].iloc[0], example_interface.name)

    def test_get_all(self):
        """Test get all interfaces of Bras layer in the database."""
        self.mongo_db_test.insert()
        database = BrasMongoQuery(uri=self.mongo_db_test.uri)
        interfaces = database.get_interfaces()
        print(interfaces)
        self.mongo_db_test.clean()
        self.assertFalse(interfaces.empty)


if __name__ == "__main__":
    unittest.main()