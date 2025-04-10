from storage.constant.tables import TableNameDatabase
from storage.constant.fields import CachingFieldDatabase
from storage.database.factory.mongo import MongoDatabaseFactory
from storage.database.product.mongo import MongoDatabase
from storage.querys.caching.caching import CachingQuery
from model.caching import CachingModel
from utils.config import ConfigurationHandler
from utils.log import LogHandler


class MongoCachingQuery(CachingQuery):
    """Mongo query class for caching table."""

    __instance: "MongoCachingQuery | None" = None
    __database: MongoDatabase

    def __new__(cls) -> "MongoCachingQuery":
        if not cls.__instance:
            cls.__instance = super(MongoCachingQuery, cls).__new__(cls)
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

    def new_interface(self, new: CachingModel) -> bool:
        try:
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.CACHING)
                data = new.model_dump()
                response = collection.insert_one(data)
                return response.acknowledged
            else:
                raise Exception("Database not connected.")
        except Exception as e:
            LogHandler.log(f"Failed to create new interface. {e}", path=__file__, err=True)
            return False

    def get_interface(self, interface: str) -> dict | None:
        try:
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.CACHING)
                result = collection.find_one({CachingFieldDatabase.INTERFACE: interface})
                if result:
                    return result
                else:
                    return None
            else:
                raise Exception("Database not connected.")
        except Exception as e:
            LogHandler.log(f"Failed to get interface. {e}", path=__file__, err=True)
            return None
