import unittest
import random
from datetime import datetime
from unittest.mock import MagicMock
from model.caching import CachingModel
from database.querys.caching.mongo import MongoCachingQuery
from database.querys.caching.postgres import PostgresCachingQuery


class TestCachingOperation(unittest.TestCase):
    def test_insert_interface_mongo(self):
        """Test insert a new interface of Caching layer in mongo database."""
        mock_interface = MagicMock()
        mock_interface.caching_model.return_value = CachingModel(
            id=None,
            name="interface_test_" + str(random.randint(0, 1000)),
            service="service_test_" + str(random.randint(0, 1000)),
            capacity=0,
            createAt=datetime.now().strftime("%Y-%m-%d")
        )

        database = MongoCachingQuery()
        
        response = database.new_interface(new=mock_interface.caching_model())
        self.assertTrue(response)

    def test_insert_interface_postgres(self):
        """Test insert a new interface of Borde layer in postgres database."""
        mock_interface = MagicMock()
        mock_interface.caching_model.return_value = CachingModel(
            id=None,
            name="interface_test_" + str(random.randint(0, 1000)),
            service="service_test_" + str(random.randint(0, 1000)),
            capacity=0,
            createAt=datetime.now().strftime("%Y-%m-%d")
        )

        database = PostgresCachingQuery()
        
        response = database.new_interface(new=mock_interface.caching_model())
        self.assertTrue(response)

    def test_get_interface_mongo(self):
        """Test get an interface of Borde layer in mongo database."""
        mock_interface = MagicMock()
        interface_example = CachingModel(
            id=None,
            name="interface_test_" + str(random.randint(0, 1000)),
            service="service_test_" + str(random.randint(0, 1000)),
            capacity=0,
            createAt=datetime.now().strftime("%Y-%m-%d")
        )
        mock_interface.caching_model.return_value = interface_example

        database = MongoCachingQuery()
        response = database.new_interface(new=mock_interface.caching_model())
        self.assertTrue(response)

        database = MongoCachingQuery()
        interface = database.get_interface(name=interface_example.name)
        self.assertIsNotNone(interface)
        self.assertEqual(interface.name, interface_example.name)

    def test_get_interface_postgres(self):
        """Test get an interface of Borde layer in postgres database."""
        mock_interface = MagicMock()
        interface_example = CachingModel(
            id=None,
            name="interface_test_" + str(random.randint(0, 1000)),
            service="service_test_" + str(random.randint(0, 1000)),
            capacity=0,
            createAt=datetime.now().strftime("%Y-%m-%d")
        )
        mock_interface.caching_model.return_value = interface_example

        database = PostgresCachingQuery()
        response = database.new_interface(new=mock_interface.caching_model())
        self.assertTrue(response)

        database = PostgresCachingQuery()
        interface = database.get_interface(name=interface_example.name)
        self.assertIsNotNone(interface)
        self.assertEqual(interface.name, interface_example.name)


if __name__ == "__main__":
    unittest.main()