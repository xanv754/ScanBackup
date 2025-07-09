import pandas as pd
from datetime import datetime, timedelta
from systemgrd.constants import header_bbip, header_daily_report, LayerName
from systemgrd.database import BBIPQuery, CachingMongoQuery, DailyReportQuery, DailyReportMongoQuery
from systemgrd.handler.scan import ScanHandler
from systemgrd.utils import Validate, log


class CachingHandler(ScanHandler):
    """Class to get data of caching layer."""

    __error_connection: bool = False
    caching_query: BBIPQuery
    daily_query: DailyReportQuery

    def __init__(self, uri: str | None = None):
        try:
            self.caching_query = CachingMongoQuery(uri=uri)
            self.daily_query = DailyReportMongoQuery(uri=uri)
        except Exception as e:
            log.error(f"Caching handler. Failed connecting to the database. {e}")
            self.__error_connection = True

    def get_all_interfaces(self):
        try:
            if self.__error_connection: 
                raise Exception("An error occurred while connecting to the database. The method has skipped.")
            df_interfaces = self.caching_query.get_interfaces()
        except Exception as e:
            log.error(f"Caching handler. Failed to get all interfaces of caching layer. {e}")
            return pd.DataFrame(columns=header_bbip)
        else:
            return df_interfaces
        
    def get_all_interfaces_by_date(self, date: str):
        try:
            if self.__error_connection: 
                raise Exception("An error occurred while connecting to the database. The method has skipped.")
            if not Validate.date(date): raise Exception("The date is not valid.")
            df_interfaces = self.caching_query.get_interfaces_by_date(date=date)
        except Exception as e:
            log.error(f"Caching handler. Failed to get all interfaces of caching layer. {e}")
            return pd.DataFrame(columns=header_bbip)
        else:
            return df_interfaces
        
    def get_all_daily_report(self, date: str | None = None):
        try:
            if self.__error_connection: 
                raise Exception("An error occurred while connecting to the database. The method has skipped.")
            if date and not Validate.date(date): raise Exception("The date is not valid.")
            if not date: date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            df_daily_report = self.daily_query.get_report(layer_type=LayerName.CACHING, date=date)
        except Exception as e:
            log.error(f"Caching handler. Failed to get all daily report of caching layer. {e}")
            return pd.DataFrame(columns=header_daily_report)
        else:
            return df_daily_report