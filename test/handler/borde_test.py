import unittest
import random
import pandas as pd
from datetime import datetime
from model.boder import BordeModel
from handler.borde import BordeHandler
from test import DatabaseMongoTest, ModelBordeTypeTest, LayerTypeTest


class TestMongoBordeHandler(unittest.TestCase):
    test_database: DatabaseMongoTest = DatabaseMongoTest()
    test_interface: BordeModel = BordeModel(
        id=None,
        name="interface_test_" + str(random.randint(0, 1000)),
        model=ModelBordeTypeTest.CISCO,
        capacity=0,
        createAt=datetime.now().strftime("%Y-%m-%d")
    )

    def test_get_all_interfaces(self):
        """Test get all interfaces of borde layer converted in a dataframe."""
        self.test_database.insert(table=LayerTypeTest.BORDE, data=self.test_interface.model_dump())
        bordeHandler = BordeHandler()
        data = bordeHandler.get_all_interfaces()
        self.test_database.clean(table=LayerTypeTest.BORDE)

        self.assertFalse(data.empty)


if __name__ == "__main__":
    unittest.main()