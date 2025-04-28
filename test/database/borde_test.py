import unittest
import random
from datetime import datetime
from unittest.mock import MagicMock
from model.boder import BordeModel
from database.querys.borde.mongo import MongoBordeQuery
from database.querys.borde.postgres import PostgresBordeQuery
from test import DatabasePostgresTest, DatabaseMongoTest, ModelBordeTypeTest, LayerTypeTest


class TestMongoBordeOperation(unittest.TestCase):
    test_database: DatabaseMongoTest = DatabaseMongoTest()
    test_interface: BordeModel = BordeModel(
        id=None,
        name="interface_test_" + str(random.randint(0, 1000)),
        model=ModelBordeTypeTest.CISCO,
        capacity=0,
        createAt=datetime.now().strftime("%Y-%m-%d")
    )

    def test_insert_interface(self):
        """Test insert a new interface of Borde layer in the MongoDB."""
        database = MongoBordeQuery()
        response = database.new_interface(new=self.test_interface)
        self.test_database.clean(table=LayerTypeTest.BORDE)

        self.assertTrue(response)

    def test_get_interface(self):
        """Test get an interface of Borde layer in the MongoDB."""
        self.test_database.insert(table=LayerTypeTest.BORDE, data=self.test_interface.model_dump())
        database = MongoBordeQuery()
        interface = database.get_interface(name=self.test_interface.name)
        self.test_database.clean(table=LayerTypeTest.BORDE)

        self.assertIsNotNone(interface)
        self.assertEqual(interface.name, self.test_interface.name)

    def test_get_interfaces(self):
        """Test get all interfaces of Borde layer in the MongoDB."""
        self.test_database.insert(table=LayerTypeTest.BORDE, data=self.test_interface.model_dump())
        database = MongoBordeQuery()
        interfaces = database.get_interfaces()
        self.test_database.clean(table=LayerTypeTest.BORDE)
        
        self.assertIsNotNone(interfaces)

# class TestPostgresBordeOperation(unittest.TestCase):
#     def test_insert_interface(self):
#         """Test insert a new interface of Borde layer in the PostgreSQL."""
#         mock_interface = MagicMock()
#         mock_interface.border_model.return_value = BordeModel(
#             id=None,
#             name="interface_test_" + str(random.randint(0, 1000)),
#             model=ModelBordeTypeTest.CISCO,
#             capacity=0,
#             createAt=datetime.now().strftime("%Y-%m-%d")
#         )

#         database = PostgresBordeQuery()
        
#         response = database.new_interface(new=mock_interface.border_model())
#         self.assertTrue(response)

#     def test_get_interface(self):
#         """Test get an interface of Borde layer in the PostgreSQL."""
#         mock_interface = MagicMock()
#         interface_example = BordeModel(
#             id=None,
#             name="interface_test_" + str(random.randint(0, 1000)),
#             model=ModelBordeTypeTest.CISCO,
#             capacity=0,
#             createAt=datetime.now().strftime("%Y-%m-%d")
#         )
#         mock_interface.border_model.return_value = interface_example

#         database = PostgresBordeQuery()
#         response = database.new_interface(new=mock_interface.border_model())
#         self.assertTrue(response)

#         database = PostgresBordeQuery()
#         interface = database.get_interface(name=interface_example.name)
#         self.assertIsNotNone(interface)
#         self.assertEqual(interface.name, interface_example.name)

#     def test_get_interfaces(self):
#         """Test get all interfaces of Borde layer in the PostgreSQL."""
#         mock_interface = MagicMock()
#         interface_example = BordeModel(
#             id=None,
#             name="interface_test_" + str(random.randint(0, 1000)),
#             model=ModelBordeTypeTest.CISCO,
#             capacity=0,
#             createAt=datetime.now().strftime("%Y-%m-%d")
#         )
#         mock_interface.border_model.return_value = interface_example

#         database = PostgresBordeQuery()
#         response = database.new_interface(new=mock_interface.border_model())
#         self.assertTrue(response)

#         database = PostgresBordeQuery()
#         interfaces = database.get_interfaces()
#         self.assertIsNotNone(interfaces)


if __name__ == "__main__":
    unittest.main()