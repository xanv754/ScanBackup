import unittest
import random
from datetime import datetime
from unittest.mock import MagicMock
from model.caching import CachingModel
from database.querys.caching.mongo import MongoCachingQuery
from database.querys.caching.postgres import PostgresCachingQuery
from test import DatabasePostgresTest, DatabaseMongoTest, LayerTypeTest


class TestMongoCachingOperation(unittest.TestCase):
    test_database: DatabaseMongoTest = DatabaseMongoTest()
    test_interface: CachingModel = CachingModel(
        id=None,
        name="interface_test_" + str(random.randint(0, 1000)),
        service="service_test_" + str(random.randint(0, 1000)),
        capacity=0,
        createAt=datetime.now().strftime("%Y-%m-%d")
    )

    def test_insert_interface(self):
        """Test insert a new interface of Caching layer in the MongoDB."""
        database = MongoCachingQuery() 
        response = database.new_interface(new=self.test_interface)
        self.test_database.clean(table=LayerTypeTest.CACHING)

        self.assertTrue(response)

    def test_get_interface(self):
        """Test get an interface of Borde layer in the MongoDB."""
        self.test_database.insert(table=LayerTypeTest.CACHING, data=self.test_interface.model_dump())
        database = MongoCachingQuery()
        interface = database.get_interface(name=self.test_interface.name)
        self.test_database.clean(table=LayerTypeTest.CACHING)
        
        self.assertIsNotNone(interface)
        self.assertEqual(interface.name, self.test_interface.name)


# class TestPostgresCachingOperation(unittest.TestCase):
#     def test_insert_interface(self):
#         """Test insert a new interface of Borde layer in the PostgreSQL."""
#         mock_interface = MagicMock()
#         mock_interface.caching_model.return_value = CachingModel(
#             id=None,
#             name="interface_test_" + str(random.randint(0, 1000)),
#             service="service_test_" + str(random.randint(0, 1000)),
#             capacity=0,
#             createAt=datetime.now().strftime("%Y-%m-%d")
#         )

#         database = PostgresCachingQuery()
        
#         response = database.new_interface(new=mock_interface.caching_model())
#         self.assertTrue(response)

#     def test_get_interface(self):
#         """Test get an interface of Borde layer in the PostgreSQL."""
#         mock_interface = MagicMock()
#         interface_example = CachingModel(
#             id=None,
#             name="interface_test_" + str(random.randint(0, 1000)),
#             service="service_test_" + str(random.randint(0, 1000)),
#             capacity=0,
#             createAt=datetime.now().strftime("%Y-%m-%d")
#         )
#         mock_interface.caching_model.return_value = interface_example

#         database = PostgresCachingQuery()
#         response = database.new_interface(new=mock_interface.caching_model())
#         self.assertTrue(response)

#         database = PostgresCachingQuery()
#         interface = database.get_interface(name=interface_example.name)
#         self.assertIsNotNone(interface)
#         self.assertEqual(interface.name, interface_example.name)


if __name__ == "__main__":
    unittest.main()