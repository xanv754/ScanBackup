import unittest
from scanbackup.infrastructure.persistence.mongodb.connections.database import (
    MongoDatabase,
)
from scanbackup.shared import Configuration


class TestMongoDB(unittest.TestCase):
    def test_create_collection(self) -> None:
        try:
            config = Configuration()
            cfg_db = config.get_cfg_database()
            cfg_layers = config.get_cfg_layers()

            mongodb = MongoDatabase()
            mongodb.set_uri(cfg_db)

            mongodb.create_collections(config=cfg_layers)
        except Exception:
            self.assertTrue(False)
        else:
            self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
