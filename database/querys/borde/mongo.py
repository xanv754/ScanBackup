from typing import List
from database.constant.tables import TableNameDatabase
from database.constant.fields import BordeFieldDatabase
from database.libs.factory.mongo import MongoDatabaseFactory
from database.libs.product.mongo import MongoDatabase
from database.querys.borde.borde import BordeQuery
from model.boder import BordeModel
from utils.config import ConfigurationHandler
from utils.trasform import BordeResponseTrasform
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

    def set_database(self, uri: str) -> None:
        try:
            if self.__database.connected:
                self.__database.close_connection()
            new_database = MongoDatabaseFactory().get_database(uri=uri)
            self.__database = new_database
        except Exception as e:
            LogHandler.log(f"Failed to connect to MongoDB database. {e}", path=__file__, err=True)

    def close_connection(self) -> None:
        self.__database.close_connection()

    def new_interface(self, new: BordeModel) -> bool:
        try:
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.BORDE)
                data = new.model_dump(exclude={BordeFieldDatabase.ID})
                response = collection.insert_one(data)
            else:
                raise Exception("Database not connected.")
        except Exception as e:
            LogHandler.log(f"Failed to create new interface. {e}", path=__file__, err=True)
            return False
        else:
            return response.acknowledged

    def get_interface(self, name: str) -> BordeModel | None:
        try:
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.BORDE)
                result = collection.find_one({BordeFieldDatabase.NAME: name})
                if result:
                    data = BordeResponseTrasform.default_model_mongo([result])
                    if data: return data[0]
                return None
            else:
                raise Exception("Database not connected.")
        except Exception as e:
            LogHandler.log(f"Failed to get interface. {e}", path=__file__, err=True)
            return None
        
    def get_interfaces(self) -> List[BordeModel]:
        try:
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.BORDE)
                cursor = collection.find()
                result: List[BordeModel] = BordeResponseTrasform.default_model_mongo(cursor)
                self.__database.close_connection()
        except Exception as e:
            LogHandler.log(f"Failed to get all interfaces. {e}", path=__file__, err=True)
            return []
        else:
            return result
