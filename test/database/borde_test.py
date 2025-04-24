import os
import unittest
import random
from datetime import datetime
from unittest.mock import MagicMock
from dotenv import load_dotenv
from constants.group import ModelBordeType
from model.boder import BordeModel
from database.querys.borde.mongo import MongoBordeQuery
from database.querys.borde.postgres import PostgresBordeQuery


load_dotenv(override=True)


URI_TEST_MONGO = os.getenv("URI_TEST_MONGO")
URI_TEST_POSTGRES = os.getenv("URI_TEST_POSTGRES")

class TestBordeOperation(unittest.TestCase):
    def test_insert_interface_mongo(self):
        """Test insert a new interface of Borde layer in mongo database."""
        mock_interface = MagicMock()
        mock_interface.border_model.return_value = BordeModel(
            id=None,
            name="interface_test_" + str(random.randint(0, 1000)),
            model=ModelBordeType.CISCO,
            capacity=0,
            createAt=datetime.now().strftime("%Y-%m-%d")
        )

        database = MongoBordeQuery()
        database.set_database(uri=URI_TEST_MONGO)
        
        response = database.new_interface(new=mock_interface.border_model())
        self.assertTrue(response)

    def test_insert_interface_postgres(self):
        """Test insert a new interface of Borde layer in postgres database."""
        mock_interface = MagicMock()
        mock_interface.border_model.return_value = BordeModel(
            id=None,
            name="interface_test_" + str(random.randint(0, 1000)),
            model=ModelBordeType.CISCO,
            capacity=0,
            createAt=datetime.now().strftime("%Y-%m-%d")
        )

        database = PostgresBordeQuery()
        database.set_database(uri=URI_TEST_POSTGRES)
        
        response = database.new_interface(new=mock_interface.border_model())
        self.assertTrue(response)

    def test_get_interface_mongo(self):
        """Test get an interface of Borde layer in mongo database."""
        mock_interface = MagicMock()
        interface_example = BordeModel(
            id=None,
            name="interface_test_" + str(random.randint(0, 1000)),
            model=ModelBordeType.CISCO,
            capacity=0,
            createAt=datetime.now().strftime("%Y-%m-%d")
        )
        mock_interface.border_model.return_value = interface_example

        database = MongoBordeQuery()
        database.set_database(uri=URI_TEST_MONGO)
        response = database.new_interface(new=mock_interface.border_model())
        self.assertTrue(response)

        database = MongoBordeQuery()
        database.set_database(uri=URI_TEST_MONGO)
        interface = database.get_interface(name=interface_example.name)
        self.assertIsNotNone(interface)
        self.assertEqual(interface.name, interface_example.name)

    def test_get_interface_postgres(self):
        """Test get an interface of Borde layer in postgres database."""
        mock_interface = MagicMock()
        interface_example = BordeModel(
            id=None,
            name="interface_test_" + str(random.randint(0, 1000)),
            model=ModelBordeType.CISCO,
            capacity=0,
            createAt=datetime.now().strftime("%Y-%m-%d")
        )
        mock_interface.border_model.return_value = interface_example

        database = PostgresBordeQuery()
        database.set_database(uri=URI_TEST_POSTGRES)
        response = database.new_interface(new=mock_interface.border_model())
        self.assertTrue(response)

        database = PostgresBordeQuery()
        database.set_database(uri=URI_TEST_POSTGRES)
        interface = database.get_interface(name=interface_example.name)
        self.assertIsNotNone(interface)
        self.assertEqual(interface.name, interface_example.name)

    def test_get_interfaces_mongo(self):
        """Test get all interfaces of Borde layer in mongo database."""
        mock_interface = MagicMock()
        interface_example = BordeModel(
            id=None,
            name="interface_test_" + str(random.randint(0, 1000)),
            model=ModelBordeType.CISCO,
            capacity=0,
            createAt=datetime.now().strftime("%Y-%m-%d")
        )
        mock_interface.border_model.return_value = interface_example

        database = MongoBordeQuery()
        database.set_database(uri=URI_TEST_MONGO)
        response = database.new_interface(new=mock_interface.border_model())
        self.assertTrue(response)

        database = MongoBordeQuery()
        database.set_database(uri=URI_TEST_MONGO)
        interfaces = database.get_interfaces()
        self.assertIsNotNone(interfaces)

    def test_get_interfaces_postgres(self):
        """Test get all interfaces of Borde layer in postgres database."""
        mock_interface = MagicMock()
        interface_example = BordeModel(
            id=None,
            name="interface_test_" + str(random.randint(0, 1000)),
            model=ModelBordeType.CISCO,
            capacity=0,
            createAt=datetime.now().strftime("%Y-%m-%d")
        )
        mock_interface.border_model.return_value = interface_example

        database = PostgresBordeQuery()
        database.set_database(uri=URI_TEST_POSTGRES)
        response = database.new_interface(new=mock_interface.border_model())
        self.assertTrue(response)

        database = PostgresBordeQuery()
        database.set_database(uri=URI_TEST_POSTGRES)
        interfaces = database.get_interfaces()
        self.assertIsNotNone(interfaces)


if __name__ == "__main__":
    unittest.main()