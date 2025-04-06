from storage.constant.tables import TableNameDatabase
from storage.constant.fields import BordeFieldDatabase
from storage.database.factory.mongo import MongoDatabaseFactory
from storage.database.product.mongo import MongoDatabase
from storage.querys.borde.borde import BordeQuery
from model.boder import BorderModel
from utils.config import ConfigurationHandler
from utils.log import LogHandler


class MongoBordeQuery(BordeQuery):
    """Mongo query class for borde table."""

    __instance: "MongoBordeQuery | None" = None
    __database: MongoDatabase

    def __new__(cls) -> "MongoBordeQuery":
        if not cls.__instance:
            cls.__instance = super(MongoBordeQuery, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        try:
            if not hasattr(self, "__initialized"):
                self.__initialized = True
                config = ConfigurationHandler()
                database = MongoDatabaseFactory().get_database(uri=config.uri_mongo)
                self.__database = database
        except Exception as e:
            LogHandler.log(f"Failed to connect to MongoDB database. {e}", path=__file__, err=True)

    def new_interface(self, new: BorderModel) -> bool:
        try:
            collection = self.__database.get_cursor(table=TableNameDatabase.BORDE)
            data = new.model_dump()
            response = collection.insert_one(data)
            return response.acknowledged
        except Exception as e:
            LogHandler.log(f"Failed to create new interface. {e}", path=__file__, err=True)
            return False

    def get_interface(self, interface: str) -> dict | None:
        try:
            collection = self.__database.get_cursor(table=TableNameDatabase.BORDE)
            result = collection.find_one({BordeFieldDatabase.INTERFACE: interface})
            if result:
                return result
            else:
                return None
        except Exception as e:
            LogHandler.log(f"Failed to get interface. {e}", path=__file__, err=True)
            return None
