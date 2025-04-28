import unittest
import random
from datetime import datetime
from model.bras import BrasModel
from handler.bras import BrasHandler
from test import DatabasePostgresTest, DatabaseMongoTest, LayerTypeTest, BrasTypeTest


class TestMongoBrasHandler(unittest.TestCase):
    test_database: DatabaseMongoTest = DatabaseMongoTest()
    test_interface: BrasModel = BrasModel(
        id=None,
        name="interface_test_" + str(random.randint(0, 1000)),
        type=BrasTypeTest.UPLINK,
        capacity=0,
        createAt=datetime.now().strftime("%Y-%m-%d")
    )

    def test_get_all_interfaces(self):
        """Test get all interfaces of bras layer converted in a dataframe."""
        self.test_database.insert(table=LayerTypeTest.BRAS, data=self.test_interface.model_dump())
        brasHandler = BrasHandler()
        data = brasHandler.get_all_interfaces()
        self.test_database.clean(table=LayerTypeTest.BRAS)

        self.assertFalse(data.empty)


if __name__ == "__main__":
    unittest.main()