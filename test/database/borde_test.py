import os
import unittest
from dotenv import load_dotenv
from controllers.borde import BordeController
from model.boder import BorderModel
from storage.querys.borde.mongo import MongoBordeQuery


load_dotenv(override=True)

URI_TEST_MONGO = os.getenv("URI_MONGO")
INTERFACE_EXAMPLE = BorderModel(
    interface="interface_test",
    model="interface_model",
    capacity=0
)

class TestBordeResponse(unittest.TestCase):
    def test_insert_interface(self):
        """Test insert a new interface of Borde layer in the database."""
        database = MongoBordeQuery()
        database.set_database(uri=URI_TEST_MONGO)
        response = database.new_interface(new=INTERFACE_EXAMPLE)
        self.assertTrue(response)

    def test_get_interface(self):
        """Test get an interface by interface name of Borde layer in the database."""
        database = MongoBordeQuery()
        database.set_database(uri=URI_TEST_MONGO)
        response = database.get_interface(interface=INTERFACE_EXAMPLE.interface)
        self.assertTrue(response)
        self.assertEqual(response.interface, INTERFACE_EXAMPLE.interface)

    def test_get_interfaces(self):
        """Test get all interfaces of Borde layer in the database."""
        database = MongoBordeQuery()
        database.set_database(uri=URI_TEST_MONGO)
        response = database.get_interfaces()
        self.assertTrue(response)

    def test_get_traffic_by_date(self):
        """Test get all traffic by a date."""
        response = BordeController.get_traffic_by_date(date="2025-01-01")
        print(response)
        self.assertTrue(response)


if __name__ == "__main__":
    unittest.main()