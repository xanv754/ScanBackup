import pandas as pd
from datetime import timedelta, datetime
from multiprocessing import Pool
from constants import header_all_bbip, header_daily_report, LayerName, HeaderBBIP
from handler.borde import BordeHandler
from handler.bras import BrasHandler
from handler.caching import CachingHandler
from handler.rai import RaiHandler
from handler.scan import ScanHandler
from utils.validate import Validate
from utils.log import log


class BBIPHandler:
    """Class to get data of BBIP layer."""

    __error_connection: bool = False
    borde_handler: ScanHandler
    bras_handler: ScanHandler
    caching_handler: ScanHandler
    rai_handler: ScanHandler

    def __init__(self, uri: str | None = None):
        try:
            self.borde_handler = BordeHandler(uri=uri)
            self.bras_handler = BrasHandler(uri=uri)
            self.caching_handler = CachingHandler(uri=uri)
            self.rai_handler = RaiHandler(uri=uri)
        except Exception as e:
            log.error(f"BBIP handler. Failed connecting to the database. {e}")
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
            if data:
                df_interfaces = pd.concat(data, axis=0)
                df_interfaces.drop_duplicates(inplace=True)
                df_interfaces.reset_index(drop=True, inplace=True)
                return df_interfaces
            else: return pd.DataFrame(columns=header_all_bbip)
        except Exception as e:
            log.error(f"BBIP handler. Failed to get all interfaces of BBIP. {e}")
            return pd.DataFrame(columns=header_all_bbip)
        
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
            if data:
                df_interfaces = pd.concat(data, axis=0)
                df_interfaces.drop_duplicates(inplace=True)
                df_interfaces.reset_index(drop=True, inplace=True)
                return df_interfaces
            else: return pd.DataFrame(columns=header_all_bbip)
        except Exception as e:
            log.error(f"BBIP handler. Failed to get all interfaces of BBIP for date {date}. {e}")
            return pd.DataFrame(columns=header_all_bbip)

    def get_all_daily_report_by_date(self, date: str | None = None) -> pd.DataFrame:
        try:
            if self.__error_connection: 
                raise Exception("An error occurred while connecting to the database. The method has skipped.")
            if date and not Validate.date(date): raise Exception("The date is not valid.")
            df_borde = self.borde_handler.get_all_daily_report(date=date)
            df_bras = self.bras_handler.get_all_daily_report(date=date)
            df_caching = self.caching_handler.get_all_daily_report(date=date)
            df_rai = self.rai_handler.get_all_daily_report(date=date)
            data: list[pd.DataFrame] = [df for df in [df_borde, df_bras, df_caching, df_rai] if not df.empty]
            if data:
                df_daily_report = pd.concat(data, axis=0)
                df_daily_report.drop_duplicates(inplace=True)
                df_daily_report.reset_index(drop=True, inplace=True)
                return df_daily_report
            else: return pd.DataFrame(columns=header_daily_report)
        except Exception as e:
            log.error(f"BBIP handler. Failed to get all daily reports of BBIP. {e}")
            return pd.DataFrame(columns=header_daily_report)
        
    def get_all_daily_data_on_week(self) -> pd.DataFrame:
        try:
            if self.__error_connection: 
                raise Exception("An error occurred while connecting to the database. The method has skipped.")
            df_daily_report = pd.DataFrame(columns=header_daily_report)
            date = (datetime.now() - timedelta(days=datetime.now().weekday() + 1))
            while date.strftime("%Y-%m-%d") != datetime.now().strftime("%Y-%m-%d"):
                df = self.get_all_daily_report_by_date(date=date.strftime("%Y-%m-%d"))
                if df_daily_report.empty and not df.empty: df_daily_report = df
                elif not df.empty: 
                    df_daily_report = pd.concat([df_daily_report, df], ignore_index=True)
                    df_daily_report.drop_duplicates(inplace=True)
                    df_daily_report.reset_index(drop=True, inplace=True)
                date = date + timedelta(days=1)
        except Exception as e:
            log.error(f"BBIP handler. Failed to get all daily reports of BBIP. {e}")
            return pd.DataFrame()
        else:
            return df_daily_report
        
    def get_all_daily_data_by_first_month(self, date_to: int | None = None) -> pd.DataFrame:
        try:
            if self.__error_connection: 
                raise Exception("An error occurred while connecting to the database. The method has skipped.")
            df_daily_report = pd.DataFrame(columns=header_daily_report)
            if not date_to: date_to = datetime.now().day
            if date_to < 10: date_to = f"0{date_to}"
            last_date = datetime.strptime(datetime.now().strftime("%Y-%m-%d")[:-3] + "-" + str(date_to))
            first_date = datetime.strptime(datetime.now().strftime("%Y-%m-%d")[:-3] + "-01")
            while first_date.strftime("%Y-%m-%d") != last_date:
                df = self.get_all_daily_report_by_date(date=first_date.strftime("%Y-%m-%d"))
                if df_daily_report.empty and not df.empty: df_daily_report = df
                elif not df.empty: 
                    df_daily_report = pd.concat([df_daily_report, df], ignore_index=True)
                    df_daily_report.drop_duplicates(inplace=True)
                    df_daily_report.reset_index(drop=True, inplace=True)
                first_date = first_date + timedelta(days=1)
        except Exception as e:
            log.error(f"Traffic handler. Failed to get all daily reports of BBIP. {e}")
            return pd.DataFrame()
        else:
            return df_daily_report
        
    def get_all_daily_data_by_days_before(self, day_before: int = 30) -> pd.DataFrame:
        try:
            if self.__error_connection: 
                raise Exception("An error occurred while connecting to the database. The method has skipped.")
            df_daily_report = pd.DataFrame(columns=header_daily_report)
            for day in range(day_before, 0, -1):
                date = (datetime.now() - timedelta(days=day)).strftime("%Y-%m-%d")
                df = self.get_all_daily_report_by_date(date=date)
                if df_daily_report.empty and not df.empty: df_daily_report = df
                elif not df.empty: 
                    df_daily_report = pd.concat([df_daily_report, df], axis=0)
                    df_daily_report.drop_duplicates(inplace=True)
                    df_daily_report.reset_index(drop=True, inplace=True)
        except Exception as e:
            log.error(f"BBIP handler. Failed to get all daily reports of BBIP. {e}")
            return pd.DataFrame()
        else:
            return df_daily_report