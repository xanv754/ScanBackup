import pandas as pd
from datetime import timedelta, datetime
from constants import header_bbip, header_daily_report
from handler.borde import BordeHandler
from handler.bras import BrasHandler
from handler.caching import CachingHandler
from handler.rai import RaiHandler
from utils.log import log


class BBIPHandler:
    """Class to get data of BBIP layer."""

    __error_connection: bool = False
    borde_handler: BordeHandler
    bras_handler: BrasHandler
    caching_handler: CachingHandler
    rai_handler: RaiHandler

    def __init__(self, uri: str | None = None):
        try:
            self.borde_handler = BordeHandler(uri=uri)
            self.bras_handler = BrasHandler(uri=uri)
            self.caching_handler = CachingHandler(uri=uri)
            self.rai_handler = RaiHandler(uri=uri)
        except Exception as e:
            log.error(f"Borde handler. Failed connecting to the database. {e}")
            self.__error_connection = True

    def get_all_interfaces(self) -> pd.DataFrame:
        """Get all data interfaces of all layers."""
        try:
            if self.__error_connection: 
                raise Exception("An error occurred while connecting to the database. The method has skipped.")
            df_borde = self.borde_handler.get_all_interfaces()
            df_bras = self.bras_handler.get_all_interfaces()
            df_caching = self.caching_handler.get_all_interfaces()
            df_rai = self.rai_handler.get_all_interfaces()
            df_interfaces = pd.concat([df_borde, df_bras, df_caching, df_rai], axis=0)
        except Exception as e:
            log.error(f"Borde handler. Failed to get all interfaces of borde layer. {e}")
            return pd.DataFrame(columns=header_bbip)
        else:
            return df_interfaces

    def get_all_daily_report(self, date: str | None = None) -> pd.DataFrame:
        try:
            if self.__error_connection: 
                raise Exception("An error occurred while connecting to the database. The method has skipped.")
            df_borde = self.borde_handler.get_all_daily_report(date=date)
            df_bras = self.bras_handler.get_all_daily_report(date=date)
            df_caching = self.caching_handler.get_all_daily_report(date=date)
            df_rai = self.rai_handler.get_all_daily_report(date=date)
            df_daily_report = pd.concat([df_borde, df_bras, df_caching, df_rai], axis=0)
        except Exception as e:
            log.error(f"Borde handler. Failed to get all daily report of borde layer. {e}")
            return pd.DataFrame(columns=header_daily_report)
        else:
            return df_daily_report
        
    def get_all_daily_report_by_days_before(self, day_before: int = 30) -> pd.DataFrame:
        """Get all daily report of all layers by dates before to today.

        Parameters
        ----------
        day_before: int, default 30
            Number of days before to today.
        """
        try:
            if self.__error_connection: 
                raise Exception("An error occurred while connecting to the database. The method has skipped.")
            df_daily_report = pd.DataFrame(columns=header_daily_report)
            for day in range(day_before, 0, -1):
                date = (datetime.now() - timedelta(days=day)).strftime("%Y-%m-%d")
                df = self.get_all_daily_report(date=date)
                if df_daily_report.empty: df_daily_report = df
                else: df_daily_report = pd.concat([df_daily_report, df], axis=0)
        except Exception as e:
            log.error(f"Traffic handler. Failed to get traffic layer by days before. {e}")
            return pd.DataFrame()
        else:
            return df_daily_report