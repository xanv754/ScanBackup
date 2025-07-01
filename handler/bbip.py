import pandas as pd
from datetime import timedelta, datetime
from constants import header_all_bbip, header_daily_report, LayerName, HeaderBBIP
from handler.scan import ScanHandler
from handler.borde import BordeHandler
from handler.bras import BrasHandler
from handler.caching import CachingHandler
from handler.rai import RaiHandler
from utils.validate import Validate
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
        try:
            if self.__error_connection: 
                raise Exception("An error occurred while connecting to the database. The method has skipped.")
            df_borde = self.borde_handler.get_all_interfaces()
            df_borde[HeaderBBIP.TYPE_LAYER] = LayerName.BORDE
            df_bras = self.bras_handler.get_all_interfaces()
            df_bras[HeaderBBIP.TYPE_LAYER] = LayerName.BRAS
            df_caching = self.caching_handler.get_all_interfaces()
            df_caching[HeaderBBIP.TYPE_LAYER] = LayerName.CACHING
            df_rai = self.rai_handler.get_all_interfaces()
            df_rai[HeaderBBIP.TYPE_LAYER] = LayerName.RAI
            data = [df for df in [df_borde, df_bras, df_caching, df_rai] if not df.empty]
            df_interfaces = pd.concat(data, axis=0)
        except Exception as e:
            log.error(f"Borde handler. Failed to get all interfaces of borde layer. {e}")
            return pd.DataFrame(columns=header_all_bbip)
        else:
            return df_interfaces
        
    def get_all_interfaces_by_date(self, date: str) -> pd.DataFrame:
        try:
            if self.__error_connection: 
                raise Exception("An error occurred while connecting to the database. The method has skipped.")
            if not Validate.date(date): raise Exception("The date is not valid.")
            df_borde = self.borde_handler.get_all_interfaces_by_date(date=date)
            df_borde[HeaderBBIP.TYPE_LAYER] = LayerName.BORDE
            df_bras = self.bras_handler.get_all_interfaces_by_date(date=date)
            df_bras[HeaderBBIP.TYPE_LAYER] = LayerName.BRAS
            df_caching = self.caching_handler.get_all_interfaces_by_date(date=date)
            df_caching[HeaderBBIP.TYPE_LAYER] = LayerName.CACHING
            df_rai = self.rai_handler.get_all_interfaces_by_date(date=date)
            df_rai[HeaderBBIP.TYPE_LAYER] = LayerName.RAI
            data = [df for df in [df_borde, df_bras, df_caching, df_rai] if not df.empty]
            df_interfaces = pd.concat(data, axis=0)
        except Exception as e:
            log.error(f"Borde handler. Failed to get all interfaces of borde layer. {e}")
            return pd.DataFrame(columns=header_all_bbip)
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
            data = [df for df in [df_borde, df_bras, df_caching, df_rai] if not df.empty]
            df_daily_report = pd.concat(data, axis=0)
        except Exception as e:
            log.error(f"Borde handler. Failed to get all daily report of borde layer. {e}")
            return pd.DataFrame(columns=header_daily_report)
        else:
            return df_daily_report
        
    def get_all_daily_report_by_days_before(self, day_before: int = 30) -> pd.DataFrame:
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