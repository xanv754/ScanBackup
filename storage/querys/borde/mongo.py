from storage.database.factory.mongo import MongoDatabaseFactory
from storage.database.product.mongo import MongoDatabase
from storage.querys.borde.borde import BordeQuery
from utils.log import LogHandler


class MongoBordeQuery(BordeQuery):
    """Mongo query class for borde table."""
    __database: MongoDatabase

    def __init__(self):
        try:
            database = MongoDatabaseFactory().get_database(uri=self.__configuration.uri_mongo)
            self.__database = database
        except Exception as e:
            LogHandler.log(f"Failed to connect to MongoDB database. {e}", path=__file__, err=True)

    def new_interface(self, interface: str, model: str, capacity: int) -> bool:
        try:
            pass
        except Exception as e:
            LogHandler.log(f"Failed to create new interface. {e}", path=__file__, err=True)