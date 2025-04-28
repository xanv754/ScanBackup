import unittest
import random
from datetime import datetime
from model.caching import CachingModel
from handler.caching import CachingHandler
from test import DatabasePostgresTest, DatabaseMongoTest, LayerTypeTest


class TestMongoCachingHandler(unittest.TestCase):
    test_database: DatabaseMongoTest = DatabaseMongoTest()
    test_interface: CachingModel = CachingModel(
        id=None,
        name="interface_test_" + str(random.randint(0, 1000)),
        service="service_test_" + str(random.randint(0, 1000)),
        capacity=0,
        createAt=datetime.now().strftime("%Y-%m-%d")
    )

    def test_get_all_interfaces(self):
        """Test get all interfaces of caching layer converted in a dataframe."""
        self.test_database.insert(table=LayerTypeTest.CACHING, data=self.test_interface.model_dump())
        cachingHandler = CachingHandler()
        data = cachingHandler.get_all_interfaces()
        self.test_database.clean(table=LayerTypeTest.CACHING)

        self.assertFalse(data.empty)


if __name__ == "__main__":
    unittest.main()