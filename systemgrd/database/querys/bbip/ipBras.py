from typing import List
from pandas import DataFrame
from systemgrd.constants import TableName, IPBrasHistoryFieldName, header_ip_bras
from systemgrd.database.libs.database import DatabaseMongo
from systemgrd.model import IPBrasModel
from systemgrd.utils import ConfigurationHandler, log


class IPBrasMongoQuery:
    """Mongo query class for IP Bras history table."""

    _database: DatabaseMongo

    def __init__(self, uri: str | None = None, dev: bool = False):
        try:
            if not uri:
                config = ConfigurationHandler(dev=dev)
                uri = config.uri_mongo
            database = DatabaseMongo(uri=uri)
            self._database = database
        except Exception as e:
            log.error(f"Failed to connect to MongoDB database. {e}")

    def new_interface(self, collection: str, data: List[IPBrasModel]) -> bool:
        try:
            status_insert = False
            self._database.open_connection()
            if self._database.connected:
                cursor = self._database.get_cursor(table=collection)
                response = cursor.insert_many([json.model_dump() for json in data])
                status_insert = response.acknowledged
            self._database.close_connection()
        except Exception as e:
            log.error(f"Failed to create new IP Bras interfaces in {collection}. {e}")
            return False
        else:
            return status_insert

    def get_ip_history(self, bras_name: str, date: str) -> DataFrame:
        try:
            ip_history: DataFrame = DataFrame(columns=header_ip_bras)
            self._database.open_connection()
            if self._database.connected:
                cursor = self._database.get_cursor(table=TableName.IP_BRAS_HISTORY)
                result = cursor.find_one({IPBrasHistoryFieldName.BRAS_NAME: bras_name, IPBrasHistoryFieldName.DATE: date})
                if result:
                    # Crear adapter simple para IPBras si BBIPResponseAdapter no funciona
                    data = DataFrame([result])
                    if not data.empty:
                        ip_history = data
            self._database.close_connection()
            return ip_history
        except Exception as e:
            log.error(f"Failed to get IP history. {e}")
            return DataFrame(columns=header_ip_bras)

    def get_ip_histories(self) -> DataFrame:
        try:
            ip_histories: DataFrame = DataFrame(columns=header_ip_bras)
            self._database.open_connection()
            if self._database.connected:
                cursor = self._database.get_cursor(table=TableName.IP_BRAS_HISTORY)
                cursor = cursor.find()
                ip_histories = DataFrame(list(cursor))
            self._database.close_connection()
            return ip_histories
        except Exception as e:
            log.error(f"Failed to get all IP histories. {e}")
            return DataFrame(columns=header_ip_bras)

    def get_ip_histories_by_date(self, date: str) -> DataFrame:
        try:
            ip_histories: DataFrame = DataFrame(columns=header_ip_bras)
            self._database.open_connection()
            if self._database.connected:
                cursor = self._database.get_cursor(table=TableName.IP_BRAS_HISTORY)
                cursor = cursor.find({IPBrasHistoryFieldName.DATE: date})
                ip_histories = DataFrame(list(cursor))
            self._database.close_connection()
            return ip_histories
        except Exception as e:
            log.error(f"Failed to get all IP histories by date. {e}")
            return DataFrame(columns=header_ip_bras)

    def get_ip_histories_by_date_range(self, start_date: str, end_date: str) -> DataFrame:
        try:
            ip_histories: DataFrame = DataFrame(columns=header_ip_bras)
            self._database.open_connection()
            if self._database.connected:
                cursor = self._database.get_cursor(table=TableName.IP_BRAS_HISTORY)
                cursor = cursor.find({
                    IPBrasHistoryFieldName.DATE: {"$gte": start_date, "$lte": end_date}
                })
                ip_histories = DataFrame(list(cursor))
            self._database.close_connection()
            return ip_histories
        except Exception as e:
            log.error(f"Failed to get IP histories by date range. {e}")
            return DataFrame(columns=header_ip_bras)

    def get_ip_histories_by_date_with_aggregation(self, date: str) -> DataFrame:
        try:
            ip_histories: DataFrame = DataFrame(columns=header_ip_bras)
            self._database.open_connection()
            if self._database.connected:
                cursor = self._database.get_cursor(table=TableName.IP_BRAS_HISTORY)
                pipeline = [
                    {"$match": {IPBrasHistoryFieldName.DATE: date}},
                    {"$sort": {IPBrasHistoryFieldName.TIME: 1}},
                    {"$limit": 1000}
                ]
                cursor = cursor.aggregate(pipeline)
                ip_histories = DataFrame(list(cursor))
            self._database.close_connection()
            return ip_histories
        except Exception as e:
            log.error(f"Failed to get IP histories by date with aggregation. {e}")
            return DataFrame(columns=header_ip_bras)