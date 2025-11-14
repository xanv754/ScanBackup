from typing import List
from pandas import DataFrame
from scanbackup.constants import TableName, DailySummaryFieldName, header_daily
from scanbackup.database.libs.database import DatabaseMongo
from scanbackup.database.querys.daily.query import DailySummaryQuery
from scanbackup.database.utils.adapter import DailySummaryResponseAdapter
from scanbackup.model import DailySummaryModel
from scanbackup.utils import log, URIEnvironment


class DailySummaryMongoQuery(DailySummaryQuery):
    """Mongo query class for daily reports table."""

    _database: DatabaseMongo

    def __init__(self, uri: str | None = None, dev: bool = False):
        try:
            if not uri or dev:
                config = URIEnvironment(dev=dev)
                uri = config.get_uri_db()
            database = DatabaseMongo(uri=uri)
            self._database = database
        except Exception as error:
            log.error(f"Fallo al intentar conectarse a la base de datos del sistema - {error}")

    def new_report(self, data: List[DailySummaryModel]):
        try:
            status_insert = False
            self._database.open_connection()
            if self._database.connected:
                collection = self._database.get_cursor(table=TableName.DAILY_SUMMARY)
                response = collection.insert_many([json.model_dump() for json in data])
                status_insert = response.acknowledged
                self._database.close_connection()
            return status_insert
        except Exception as error:
            log.error(f"Fallo al registrar las nuevas interfaces en la colección de los reportes diarios - {error}")
            return False

    def get_report(self, layer_type: str, date: str):
        try:
            traffic: DataFrame = DataFrame(columns=header_daily)
            self._database.open_connection()
            if self._database.connected:
                collection = self._database.get_cursor(table=TableName.DAILY_SUMMARY)
                result = collection.find(
                    {
                        DailySummaryFieldName.DATE: date,
                        DailySummaryFieldName.TYPE_LAYER: layer_type,
                    }
                )
                if result:
                    data = DailySummaryResponseAdapter.to_dataframe(result)
                    if not data.empty:
                        traffic = data
                self._database.close_connection()
            return traffic
        except Exception as error:
            log.error(f"Fallo al intentar obtener la data de reportes diarios de la capa: {layer_type} del día: {date} - {error}")
            return DataFrame(columns=header_daily)
