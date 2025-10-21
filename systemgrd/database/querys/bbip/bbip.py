from typing import List
from pandas import DataFrame
from systemgrd.constants import BBIPFieldName, header_bbip
from systemgrd.database.libs.database import DatabaseMongo
from systemgrd.database.querys.bbip.query import BBIPQuery
from systemgrd.database.utils.adapter import BBIPResponseAdapter
from systemgrd.model import BBIPModel
from systemgrd.utils import ConfigurationHandler, log


class BBIPMongoQuery(BBIPQuery):
    """Mongo query class for all services of BBIP data."""

    _database: DatabaseMongo

    def __init__(self, uri: str | None = None, dev: bool = False):
        try:
            if not uri or dev:
                config = ConfigurationHandler(dev=dev)
                uri = config.uri_mongo
            database = DatabaseMongo(uri=uri)
            self._database = database
        except Exception as e:
            log.error(f"Failed to connect to MongoDB database. {e}")

    def new_interface(self, collection: str, data: List[BBIPModel]) -> bool:
        try:
            status_insert = False
            self._database.open_connection()
            if self._database.connected:
                cursor = self._database.get_cursor(table=collection)
                response = cursor.insert_many([json.model_dump() for json in data])
                status_insert = response.acknowledged
                self._database.close_connection()
        except Exception as e:
            log.error(f"Failed to create new interfaces in {collection}. {e}")
            return False
        else:
            return status_insert

    def get_interface(self, collection: str, name: str) -> DataFrame:
        try:
            interface: DataFrame = DataFrame(columns=header_bbip)
            self._database.open_connection()
            if self._database.connected:
                cursor = self._database.get_cursor(table=collection)
                result = cursor.find_one({BBIPFieldName.NAME: name})
                if result:
                    data = BBIPResponseAdapter.to_dataframe([result])
                    if not data.empty:
                        interface = data
                self._database.close_connection()
            return interface
        except Exception as e:
            log.error(f"Failed to get interface. {e}")
            return DataFrame(columns=header_bbip)

    def get_interfaces(self, collection: str) -> DataFrame:
        try:
            interfaces: DataFrame = DataFrame(columns=header_bbip)
            self._database.open_connection()
            if self._database.connected:
                cursor = self._database.get_cursor(table=collection)
                cursor = cursor.find()
                interfaces = BBIPResponseAdapter.to_dataframe(cursor)
                self._database.close_connection()
            return interfaces
        except Exception as e:
            log.error(f"Failed to get all interfaces. {e}")
            return DataFrame(columns=header_bbip)

    def get_interfaces_by_date(self, collection: str, date: str) -> DataFrame:
        try:
            interfaces: DataFrame = DataFrame(columns=header_bbip)
            self._database.open_connection()
            if self._database.connected:
                cursor = self._database.get_cursor(table=collection)
                cursor = cursor.find({BBIPFieldName.DATE: date})
                interfaces = BBIPResponseAdapter.to_dataframe(cursor)
                self._database.close_connection()
            return interfaces
        except Exception as e:
            log.error(f"Failed to get all interfaces by date. {e}")
            return DataFrame(columns=header_bbip)
