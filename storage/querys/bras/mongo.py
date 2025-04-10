from storage.constant.tables import TableNameDatabase
from storage.constant.fields import BrasFieldDatabase
from storage.database.factory.mongo import MongoDatabaseFactory
from storage.database.product.mongo import MongoDatabase
from storage.querys.bras.bras import BrasQuery
from model.bras import BrasModel
from utils.config import ConfigurationHandler
from utils.log import LogHandler


class MongoBrasQuery(BrasQuery):
    """Mongo query class for bras table."""

    __instance: "MongoBrasQuery | None" = None
    __database: MongoDatabase

    def __new__(cls) -> "MongoBrasQuery":
        if not cls.__instance:
            cls.__instance = super(MongoBrasQuery, cls).__new__(cls)
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

    def new_bras(self, new: BrasModel) -> bool:
        try:
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.BRAS)
                data = new.model_dump()
                response = collection.insert_one(data)
                return response.acknowledged
            else:
                raise Exception("Database not connected.")
        except Exception as e:
            LogHandler.log(f"Failed to create new bras. {e}", path=__file__, err=True)
            return False

    def get_bras(self, brasname: str, type: str) -> dict | None:
        try:
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.BRAS)
                result = collection.find_one(
                    {
                        BrasFieldDatabase.NAME: brasname,
                        BrasFieldDatabase.TYPE: type
                    }
                )
                if result:
                    return result
                else:
                    return None
            else:
                raise Exception("Database not connected.")
        except Exception as e:
            LogHandler.log(f"Failed to get bras. {e}", path=__file__, err=True)
            return None
