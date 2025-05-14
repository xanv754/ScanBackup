from typing import List
from database import (
    TableNameDatabase,
    RaiFieldDatabase,
    MongoDatabaseFactory,
    MongoDatabase,
    RaiQuery
)
from model import RaiModel
from utils.trasform import RaiResponseTrasform
from utils.config import ConfigurationHandler
from utils.log import log


class MongoRaiQuery(RaiQuery):
    """Mongo query class for rai table."""

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

    def new_interface(self, new: RaiModel) -> bool:
        try:
            status_insert = False
            self.__database.open_connection()
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.RAI)
                data = new.model_dump(exclude={RaiFieldDatabase.ID})
                response = collection.insert_one(data)
                status_insert = response.acknowledged
                self.__database.close_connection()
            return status_insert
        except Exception as e:
            log.error(f"Failed to create new interface. {e}")
            return False

    def get_interface(self, name: str) -> RaiModel | None:
        try:
            interface: RaiModel | None = None
            self.__database.open_connection()
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.RAI)
                result = collection.find_one({RaiFieldDatabase.NAME: name})
                self.__database.close_connection()
                if result:
                    data = RaiResponseTrasform.default_model_mongo([result])
                    if data: interface = data[0]
                self.__database.close_connection()
            return interface
        except Exception as e:
            log.error(f"Failed to get interface. {e}")
            return None

    def get_interfaces(self) -> List[RaiModel]:
        try:
            interfaces: List[RaiModel] = []
            self.__database.open_connection()
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.RAI)
                result = collection.find()
                if result: interfaces = RaiResponseTrasform.default_model_mongo(result)
                self.__database.close_connection()
            return interfaces
        except Exception as e:
            log.error(f"Failed to get all interfaces. {e}")
            return []