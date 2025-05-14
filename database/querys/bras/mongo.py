from typing import List
from database import (
    TableNameDatabase,
    BrasFieldDatabase,
    MongoDatabaseFactory,
    MongoDatabase,
    BrasQuery
)
from model import BrasModel
from utils.trasform import BrasResponseTrasform
from utils.config import ConfigurationHandler
from utils.log import log

class MongoBrasQuery(BrasQuery):
    """Mongo query class for bras table."""

    __database: MongoDatabase

    def __init__(self):
        try:
            config = ConfigurationHandler()
            factory = MongoDatabaseFactory()
            database = factory.get_database(uri=config.uri_mongo)
            self.__database = database
        except Exception as e:
            log.error(f"Failed to connect to MongoDB database. {e}")


    def set_database(self, uri: str) -> None:
        try:
            if self.__database.connected:
                self.__database.close_connection()
            new_database = MongoDatabaseFactory().get_database(uri=uri)
            self.__database = new_database
        except Exception as e:
            log.error(f"Failed to connect to MongoDB database. {e}")

    def new_interface(self, new: BrasModel) -> bool:
        try:
            status_insert = False
            self.__database.open_connection()
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.BRAS)
                data = new.model_dump(exclude={BrasFieldDatabase.ID})
                response = collection.insert_one(data)
                status_insert = response.acknowledged
                self.__database.close_connection()
            return status_insert
        except Exception as e:
            log.error(f"Failed to create new bras. {e}")
            return False

    def get_interface(self, brasname: str, type: str) -> BrasModel | None:
        try:
            interface: BrasModel | None = None
            self.__database.open_connection()
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.BRAS)
                result = collection.find_one({
                    BrasFieldDatabase.NAME: brasname,
                    BrasFieldDatabase.TYPE: type
                })
                if result:
                    data = BrasResponseTrasform.default_model_mongo([result])
                    if data: interface = data[0]
                self.__database.close_connection()
            return interface
        except Exception as e:
            log.error(f"Failed to get bras. {e}")
            return None
        
    def get_interfaces(self) -> List[BrasModel]:
        try:
            interfaces: List[BrasModel] = []
            self.__database.open_connection()
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.BRAS)
                result = collection.find()
                if result: interfaces = BrasResponseTrasform.default_model_mongo(result) 
                self.__database.close_connection()
            return interfaces
        except Exception as e:
            log.error(f"Failed to get bras. {e}")
            return []
