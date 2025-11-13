import pandas as pd
from datetime import datetime, timedelta
from scanbackup.constants import header_bbip, header_daily
from scanbackup.database import (
    BBIPQuery,
    BBIPMongoQuery,
    DailySummaryQuery,
    DailySummaryMongoQuery,
)
from scanbackup.utils import Validate, LayerDetector, log


class BBIPHandler:
    """Class to get data of borde layer."""

    _error_connection: bool = False
    bbip_query: BBIPQuery
    daily_query: DailySummaryQuery

    def __init__(self, uri: str | None = None, dev: bool = False):
        try:
            self.bbip_query = BBIPMongoQuery(uri=uri, dev=dev)
            self.daily_query = DailySummaryMongoQuery(uri=uri, dev=dev)
        except Exception as error:
            log.error(f"BBIP handler. Fallo al intentarse conectarse a la base de datos del sistema - {error}")
            self._error_connection = True

    def get_all_interfaces(self, layer: str) -> pd.DataFrame:
        """Get all data interfaces.

        :params layer: Name layer to consult.
        :type layer: str
        :returns DataFrame: Data obtained.
        """
        try:
            if self._error_connection:
                raise Exception(
                    "Ha ocurrido un error con la base de datos del sistema. La petición ha sido suspendida"
                )
            collection = LayerDetector.get_table_name(layer=layer)
            df_interfaces = self.bbip_query.get_interfaces(collection=collection)
        except Exception as error:
            log.error(f"BBIP handler. Fallo en la petición de todas las interfaces de la capa: {layer} - {error}")
            return pd.DataFrame(columns=header_bbip)
        else:
            return df_interfaces

    def get_all_interfaces_by_date(self, layer: str, date: str) -> pd.DataFrame:
        """Get all data interfaces by date.

        :params layer: Name layer to consult.
        :type layer: str
        :params date: Date of the data. Format: YYYY-MM-DD. Default is yesterday.
        :type date: str
        :returns DataFrame: Data obtained.
        """
        try:
            if self._error_connection:
                raise Exception(
                    "Ha ocurrido un error con la base de datos del sistema. La petición ha sido suspendida"
                )
            if not Validate.date(date):
                raise Exception("The date is not valid.")
            collection = LayerDetector.get_table_name(layer=layer)
            df_interfaces = self.bbip_query.get_interfaces_by_date(
                collection=collection, date=date
            )
        except Exception as error:
            log.error(f"BBIP handler. Fallo en la petición de todas las interfaces de la capa: {layer} del día: {date} - {error}")
            return pd.DataFrame(columns=header_bbip)
        else:
            return df_interfaces

    def get_all_daily_report(self, layer: str, date: str | None = None) -> pd.DataFrame:
        """Get all daily report of a date.

        :params layer: Name layer to consult.
        :type layer: str
        :params date: Date of the data. Format: YYYY-MM-DD. Default is yesterday.
        :type date: str
        :returns DataFrame: Data obtained.
        """
        try:
            if self._error_connection:
                raise Exception(
                    "Ha ocurrido un error con la base de datos del sistema. La petición ha sido suspendida"
                )
            if date and not Validate.date(date):
                raise Exception("The date is not valid.")
            elif not date:
                date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            df_daily_report = self.daily_query.get_report(layer_type=layer, date=date)
        except Exception as error:
            log.error(f"BBIP handler. Fallo en la petición de los reportes diarios de la capa: {layer} del día: {date} - {error}")
            return pd.DataFrame(columns=header_daily)
        else:
            return df_daily_report
