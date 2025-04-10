from typing import List
from storage.constant.tables import TableNameDatabase
from storage.constant.fields import BordeFieldDatabase
from storage.database.factory.mongo import MongoDatabaseFactory
from storage.database.product.mongo import MongoDatabase
from storage.querys.borde.borde import BordeQuery
from model.boder import BorderModel
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
        """Set the connection database.
        
        Parameters
        ----------
        uri : str
            New URI to connection database.
        """
        try:
            if self.__database.connected:
                self.__database.close_connection()
            new_database = MongoDatabaseFactory().get_database(uri=uri)
            self.__database = new_database
        except Exception as e:
            LogHandler.log(f"Failed to connect to MongoDB database. {e}", path=__file__, err=True)

    def new_interface(self, new: BorderModel) -> bool:
        try:
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.BORDE)
                data = new.model_dump()
                response = collection.insert_one(data)
                return response.acknowledged
            else:
                raise Exception("Database not connected.")
        except Exception as e:
            LogHandler.log(f"Failed to create new interface. {e}", path=__file__, err=True)
            return False

    def get_interface(self, interface: str) -> BorderModel | None:
        try:
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.BORDE)
                result = collection.find_one({BordeFieldDatabase.INTERFACE: interface})
                if result:
                    data = BordeResponseTrasform.trasformBorderModel([result])
                    if data: return data[0]
                return None
            else:
                raise Exception("Database not connected.")
        except Exception as e:
            LogHandler.log(f"Failed to get interface. {e}", path=__file__, err=True)
            return None
        
    def get_interfaces(self) -> List[BorderModel]:
        try:
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.BORDE)
                cursor = collection.find()
                result: List[BorderModel] = []
                for data in cursor:
                    result.append(
                        BorderModel(
                            interface=data[BordeFieldDatabase.INTERFACE],
                            model=data[BordeFieldDatabase.MODEL],
                            capacity=data[BordeFieldDatabase.CAPACITY]
                        )
                    )
                self.__database.close_connection()
                return result
        except Exception as e:
            LogHandler.log(f"Failed to get all interfaces. {e}", path=__file__, err=True)
            return []