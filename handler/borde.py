import pandas as pd
from datetime import datetime
from constants import header_bbip, header_daily_report, LayerName
from database import BBIPQuery, BordeMongoQuery, DailyReportQuery, DailyReportMongoQuery
from utils.log import log


class BordeHandler:
    """Class to get data of borde layer."""

    __error_connection: bool = False
    borde_query: BBIPQuery
    daily_query: DailyReportQuery

    def __init__(self, uri: str | None = None):
        try:
            self.borde_query = BordeMongoQuery(uri=uri)
            self.daily_query = DailyReportMongoQuery(uri=uri)
        except Exception as e:
            log.error(f"Borde handler. Failed connecting to the database. {e}")
            self.__error_connection = True

    def get_all_interfaces(self) -> pd.DataFrame:
        """Get all data interfaces of borde layer."""
        try:
            if self.__error_connection: 
                raise Exception("An error occurred while connecting to the database. The method has skipped.")
            df_interfaces = self.borde_query.get_interfaces()
        except Exception as e:
            log.error(f"Borde handler. Failed to get all interfaces of borde layer. {e}")
            return pd.DataFrame(columns=header_bbip)
        else:
            return df_interfaces
        
    def get_all_daily_report(self, date: str | None = None) -> pd.DataFrame:
        """Get all daily report of borde layer."""
        try:
            if self.__error_connection: 
                raise Exception("An error occurred while connecting to the database. The method has skipped.")
            if not date: date = datetime.now().strftime("%Y-%m-%d")
            df_daily_report = self.daily_query.get_report(layer_type=LayerName.BORDE, date=date)
        except Exception as e:
            log.error(f"Borde handler. Failed to get all daily report of borde layer. {e}")
            return pd.DataFrame(columns=header_daily_report)
        else:
            return df_daily_report