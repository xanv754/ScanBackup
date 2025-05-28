import pandas as pd
from datetime import datetime, timedelta
from constants.group import LayerType
from constants.header import HeaderDataFrame
from database import (
    BordeQuery, MongoBordeQuery, PostgresBordeQuery,
    BrasQuery, MongoBrasQuery, PostgresBrasQuery,
    CachingQuery, MongoCachingQuery, PostgresCachingQuery,
    RaiQuery, MongoRaiQuery, PostgresRaiQuery,
    DailyReportQuery, MongoDailyReportQuery, PostgresDailyReportQuery
)
from handler import BordeHandler, BrasHandler, CachingHandler, RaiHandler
from utils.validate import Validate
from utils.log import log


class DailyReportHandler:
    """Class to get history data."""

    __error_connection: bool = False
    __db_backup: bool = False
    report_query: DailyReportQuery
    borde_query: BordeQuery
    bras_query: BrasQuery
    caching_query: CachingQuery
    rai_query: RaiQuery

    def __init__(self, db_backup: bool = False):
        try:
            if not db_backup: 
                self.report_query = MongoDailyReportQuery()
                self.borde_query = MongoBordeQuery()
                self.bras_query = MongoBrasQuery()
                self.caching_query = MongoCachingQuery()
                self.rai_query = MongoRaiQuery()
            else: 
                self.__db_backup = True
                self.report_query = PostgresDailyReportQuery()
                self.borde_query = PostgresBordeQuery()
                self.bras_query = PostgresBrasQuery()
                self.caching_query = PostgresCachingQuery()
                self.rai_query = PostgresRaiQuery()
        except Exception as e:
            log.error(f"Traffic handler. Failed connecting to the database. {e}")
            self.__error_connection = True


    def __format_traffic(self, data: pd.DataFrame) -> pd.DataFrame:
        """Format a dataframe of data traffic history."""
        try:
            df = data.copy()
            df.drop(columns=[HeaderDataFrame.ID, HeaderDataFrame.TYPE_LAYER], inplace=True)
            df = df.reindex([
                HeaderDataFrame.NAME,
                HeaderDataFrame.TYPE, 
                HeaderDataFrame.CAPACITY,
                HeaderDataFrame.DATE, 
                HeaderDataFrame.IN_PROM, 
                HeaderDataFrame.OUT_PROM, 
                HeaderDataFrame.IN_MAX, 
                HeaderDataFrame.OUT_MAX
            ], axis="columns")
            df.rename(columns={
                HeaderDataFrame.NAME: HeaderDataFrame.INTERFACE
            }, inplace=True)
            return df
        except Exception as e:
            log.error(f"Traffic handler. Failed to format dataframe. {e}")
            return data
        
    def __format_layer_traffic(self, data: pd.DataFrame) -> pd.DataFrame:
        """Format a dataframe of data traffic history with data layer."""
        try:
            df = data.copy()
            df.rename(columns={
                HeaderDataFrame.MODEL: HeaderDataFrame.TYPE,
                HeaderDataFrame.SERVICE: HeaderDataFrame.TYPE
            }, inplace=True)
            df = self.__format_traffic(data=df)
            return df
        except Exception as e:
            log.error(f"Traffic handler. Failed to format dataframe. {e}")
            return data
        
    def __insert_name_layer(self, df: pd.DataFrame, layer_type: str) -> pd.DataFrame:
        """Insert interface name each interface of a layer in a dataframe."""
        try:
            df_report = df.copy()
            if not df_report.empty and layer_type == LayerType.BORDE:
                borde_handler = BordeHandler(db_backup=self.__db_backup)
                df_layer = borde_handler.get_all_interfaces()
            elif not df_report.empty and layer_type == LayerType.BRAS:
                bras_handler = BrasHandler(db_backup=self.__db_backup)
                df_layer = bras_handler.get_all_interfaces()
            elif not df_report.empty and layer_type == LayerType.CACHING:
                caching_handler = CachingHandler(db_backup=self.__db_backup)
                df_layer = caching_handler.get_all_interfaces()
            elif not df_report.empty and layer_type == LayerType.RAI:
                rai_handler = RaiHandler(db_backup=self.__db_backup)
                df_layer = rai_handler.get_all_interfaces()
            elif not df_report.empty: raise Exception(f"Layer handler not found: {layer_type}")
            if df_layer.empty: raise Exception(f"Data of layer not found: {layer_type}")
            df_report.rename(columns={HeaderDataFrame.ID_LAYER: HeaderDataFrame.ID}, inplace=True)
            df_report = df_report.merge(df_layer, how="inner", on=HeaderDataFrame.ID)
            df_report = self.__format_layer_traffic(data=df_report)
            return df_report
        except Exception as e:
            log.error(f"Traffic handler. Failed to insert name layer in dataframe. {e}")
            return pd.DataFrame()

        
    def get_daily_report_by_days_before(self, layer_type: str, day_before: int = 30) -> pd.DataFrame:
        """Get all daily report of a layer by dates before to today.

        Parameters
        ----------
        layer_type : str
            Type name of the layer to consult.
        day_before: int, default 30
            Number of days before to today.
        """
        try:
            if self.__error_connection: raise Exception("An error occurred while connecting to the database. The method has skipped.")
            if not Validate.layer_type(layer_type): raise Exception("Invalid parameter: name layer.")
            date = datetime.now().date()
            date = date - timedelta(days=1)
            dates = [(date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(day_before)]
            data = pd.DataFrame()
            for date in dates:
                traffic = self.report_query.get_report(layer_type=layer_type, date=date)
                if data.empty: data = traffic
                else: data = pd.concat([data, traffic])
            if not data.empty: data = self.__insert_name_layer(df=data, layer_type=layer_type)
            data = data.reset_index(drop=True)
            return data
        except Exception as e:
            log.error(f"Traffic handler. Failed to get traffic layer by days before. {e}")
            return pd.DataFrame()