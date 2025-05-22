from typing import List
from pandas import DataFrame
from database import (
    TableNameDatabase,
    BordeFieldDatabase,
    MongoDatabaseFactory,
    MongoDatabase,
    BordeQuery
)
from model import BordeModel
from utils.trasform import BordeResponseTrasform
from utils.config import ConfigurationHandler
from utils.log import log


class MongoBordeQuery(BordeQuery):
    """Mongo query class for borde table."""

    __database: MongoDatabase

    def __init__(self):
        try:
            config = ConfigurationHandler()
            factory = MongoDatabaseFactory()
            database = factory.get_database(uri=config.uri_mongo)
            self.__database = database
        except Exception as e:
            log.error(f"Failed to connect to MongoDB database. {e}")


    def set_database(self, uri: str):
        try:
            if self.__database.connected:
                self.__database.close_connection()
            factory = MongoDatabaseFactory()
            new_database = factory.get_database(uri=uri)
            self.__database = new_database
        except Exception as e:
            log.error(f"Failed to connect to MongoDB database. {e}")

    def new_interface(self, new: BordeModel):
        try:
            status_insert = False
            self.__database.open_connection()
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.BORDE)
                data = new.model_dump(exclude={BordeFieldDatabase.ID})
                response = collection.insert_one(data)
                status_insert = response.acknowledged
                self.__database.close_connection()
        except Exception as e:
            log.error(f"Failed to create new interface. {e}")
            return False
        else:
            return status_insert

    def get_interface(self, name: str):
        try:
            interface: DataFrame = DataFrame()
            self.__database.open_connection()
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.BORDE)
                result = collection.find_one({BordeFieldDatabase.NAME: name})
                if result:
                    data = BordeResponseTrasform.default_model_mongo([result])
                    if not data.empty: interface = data
                self.__database.close_connection()
            return interface
        except Exception as e:
            log.error(f"Failed to get interface. {e}")
            return DataFrame()
        
    def get_interfaces(self):
        try:
            interfaces: DataFrame = DataFrame()
            self.__database.open_connection()
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableNameDatabase.BORDE)
                cursor = collection.find()
                interfaces = BordeResponseTrasform.default_model_mongo(cursor)
                self.__database.close_connection()
            return interfaces
        except Exception as e:
            log.error(f"Failed to get all interfaces. {e}")
            return DataFrame()
