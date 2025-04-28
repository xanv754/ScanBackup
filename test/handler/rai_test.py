import unittest
import random
from datetime import datetime
from model.rai import RaiModel
from handler.rai import RaiHandler
from test import DatabasePostgresTest, DatabaseMongoTest, LayerTypeTest


class TestMongoRaiHandler(unittest.TestCase):
    test_database: DatabaseMongoTest = DatabaseMongoTest()
    test_interface: RaiModel = RaiModel(
        id=None,
        name="interface_test_" + str(random.randint(0, 1000)),
        capacity=0,
        createAt=datetime.now().strftime("%Y-%m-%d")
    )

    def test_get_all_interfaces(self):
        """Test get all interfaces of rai layer converted in a dataframe."""
        self.test_database.insert(table=LayerTypeTest.RAI, data=self.test_interface.model_dump())
        raiHandler = RaiHandler()
        data = raiHandler.get_all_interfaces()
        self.test_database.clean(table=LayerTypeTest.RAI)

        self.assertFalse(data.empty)


if __name__ == "__main__":
    unittest.main()