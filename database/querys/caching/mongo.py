from typing import List
from database import (
    TableNameDatabase,
    CachingFieldDatabase,
    MongoDatabaseFactory,
    MongoDatabase,
    CachingQuery
)
from model import CachingModel
from utils.config import ConfigurationHandler
from utils.trasform import CachingResponseTrasform
from utils.log import log


class MongoCachingQuery(CachingQuery):
    """Mongo query class for caching table."""

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

    def new_interface(self, new: CachingModel) -> bool:
        try:
            status_insert = False
            self.__database.open_connection()
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.CACHING)
                data = new.model_dump(exclude={CachingFieldDatabase.ID})
                response = collection.insert_one(data)
                status_insert = response.acknowledged
                self.__database.close_connection()
            return status_insert
        except Exception as e:
            log.error(f"Failed to create new interface. {e}")
            return False

    def get_interface(self, name: str) -> CachingModel | None:
        try:
            interface: CachingModel | None = None
            self.__database.open_connection()
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.CACHING)
                result = collection.find_one({CachingFieldDatabase.NAME: name})
                if result:
                    data = CachingResponseTrasform.default_model_mongo([result])
                    if data: interface = data[0]
                self.__database.close_connection()
            return interface
        except Exception as e:
            log.error(f"Failed to get interface. {e}")
            return None

    def get_interfaces(self) -> List[CachingModel]:
        try:
            interfaces: List[CachingModel] = []
            self.__database.open_connection()
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.CACHING)
                result = collection.find()
                if result: interfaces = CachingResponseTrasform.default_model_mongo(result)
                self.__database.close_connection()
            return interfaces
        except Exception as e:
            log.error(f"Failed to get all interfaces. {e}")
            return []