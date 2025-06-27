from pandas import DataFrame
from constants import TableName, BBIPFieldName, header_bbip
from database.libs.product.mongo import DatabaseMongo
from database.libs.factory.mongo import DatabaseMongoFactory
from database.querys.bbip.query import BBIPQuery
from database.utils.adapter import BBIPResponseAdapter
from model import BBIPModel
from utils.config import ConfigurationHandler
from utils.log import log


class RaiMongoQuery(BBIPQuery):
    """Mongo query class for rai table."""

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

    def new_interface(self, new: BBIPModel):
        try:
            status_insert = False
            self.__database.open_connection()
            if self.__database.connected:
                collection = self.__database.get_cursor(table=TableName.RAI)
                data = new.model_dump()
                response = collection.insert_one(data)
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
                collection = self.__database.get_cursor(table=TableName.RAI)
                result = collection.find_one({BBIPFieldName.NAME: name})
                self.__database.close_connection()
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
                collection = self.__database.get_cursor(table=TableName.RAI)
                result = collection.find()
                if result: interfaces = BBIPResponseAdapter.to_dataframe(result)
                self.__database.close_connection()
            return interfaces
        except Exception as e:
            log.error(f"Failed to get all interfaces. {e}")
            return DataFrame(columns=header_bbip)