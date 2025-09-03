from typing import List
from pandas import DataFrame
from systemgrd.constants import TableName, DailyReportFieldName, header_daily_report
from systemgrd.database.libs.database import DatabaseMongo
from systemgrd.database.querys.daily.query import DailyReportQuery
from systemgrd.database.utils.adapter import DailyReportResponseAdapter
from systemgrd.model import DailyReportModel
from systemgrd.utils import ConfigurationHandler, log


class DailyReportMongoQuery(DailyReportQuery):
    """Mongo query class for daily reports table."""

    _database: DatabaseMongo

    def __init__(self, uri: str | None = None):
        try:
            if not uri:
                config = ConfigurationHandler()
                uri = config.uri_mongo
            database = DatabaseMongo(uri=uri)
            self._database = database
        except Exception as e:
            log.error(f"Failed to connect to MongoDB database. {e}")

    def new_report(self, data: List[DailyReportModel]):
        try:
            status_insert = False
            if self._database.connected:
                collection = self._database.get_cursor(table=TableName.DAILY_REPORT)
                response = collection.insert_many([json.model_dump() for json in data])
                status_insert = response.acknowledged
                self._database.close_connection()
            return status_insert
        except Exception as e:
            log.error(f"Failed to insert a daily report. {e}")
            return False
        
    def get_report(self, layer_type: str, date: str):
        try:
            traffic: DataFrame = DataFrame(columns=header_daily_report)
            if self._database.connected:
                collection = self._database.get_cursor(table=TableName.DAILY_REPORT)
                result = collection.find({
                    DailyReportFieldName.DATE: date,
                    DailyReportFieldName.TYPE_LAYER: layer_type
                })
                if result:
                    data = DailyReportResponseAdapter.to_dataframe(result)
                    if not data.empty: traffic = data
                self._database.close_connection()
            return traffic
        except Exception as e:
            log.error(f"Failed to get daily report. {e}")
            return DataFrame(columns=header_daily_report)
