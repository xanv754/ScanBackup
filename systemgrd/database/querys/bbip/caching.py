from typing import List
from pandas import DataFrame
from systemgrd.constants import TableName, BBIPFieldName, header_bbip
from systemgrd.database.libs.product.mongo import DatabaseMongo
from systemgrd.database.libs.factory.mongo import DatabaseMongoFactory
from systemgrd.database.querys.bbip.query import BBIPQuery
from systemgrd.database.utils.adapter import BBIPResponseAdapter
from systemgrd.model import BBIPModel
from systemgrd.utils.config import ConfigurationHandler, log


class CachingMongoQuery(BBIPQuery):
    """Mongo query class for caching table."""

    __database: DatabaseMongo

    def __init__(self, uri: str | None = None):
        try:
            if not uri:
                config = ConfigurationHandler()
                uri = config.uri_mongo
            factory = DatabaseMongoFactory()
            database = factory.get_database(uri=uri)
            self.__database = database
        except Exception as e:
            log.error(f"Failed to connect to MongoDB database. {e}")


    def set_database(self, uri: str):
        try:
            if self.__database.connected:
                self.__database.close_connection()
            new_database = DatabaseMongoFactory().get_database(uri=uri)
            self.__database = new_database
        except Exception as e:
            log.error(f"Failed to connect to MongoDB database. {e}")

    def new_interface(self, data: List[BBIPModel]):
        try:
            status_insert = False
            self.__database.open_connection()
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableName.CACHING)
                response = collection.insert_many([json.model_dump() for json in data])
                status_insert = response.acknowledged
                self.__database.close_connection()
            return status_insert
        except Exception as e:
            log.error(f"Failed to create new interface. {e}")
            return False

    def get_interface(self, name: str):
        try:
            interface: DataFrame = DataFrame(columns=header_bbip)
            self.__database.open_connection()
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableName.CACHING)
                result = collection.find_one({BBIPFieldName.NAME: name})
                if result:
                    data = BBIPResponseAdapter.to_dataframe([result])
                    if not data.empty: interface = data
                self.__database.close_connection()
            return interface
        except Exception as e:
            log.error(f"Failed to get interface. {e}")
            return DataFrame(columns=header_bbip)

    def get_interfaces(self):
        try:
            interfaces: DataFrame = DataFrame()
            self.__database.open_connection()
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableName.CACHING)
                result = collection.find()
                if result: interfaces = BBIPResponseAdapter.to_dataframe(result)
                self.__database.close_connection()
            return interfaces
        except Exception as e:
            log.error(f"Failed to get all interfaces. {e}")
            return DataFrame(columns=header_bbip)
        
    def get_interfaces_by_date(self, date: str):
        try:
            interfaces: DataFrame = DataFrame(columns=header_bbip)
            self.__database.open_connection()
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableName.CACHING)
                cursor = collection.find({ BBIPFieldName.DATE: date })
                interfaces = BBIPResponseAdapter.to_dataframe(cursor)
                self.__database.close_connection()
            return interfaces
        except Exception as e:
            log.error(f"Failed to get all interfaces by date. {e}")
            return DataFrame(columns=header_bbip)