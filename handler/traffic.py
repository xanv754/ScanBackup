import pandas as pd
from typing import List
from datetime import datetime, timedelta
from constants.group import LayerType
from constants.header import HeaderDataFrame
from database import (
    BordeQuery, MongoBordeQuery, PostgresBordeQuery,
    BrasQuery, MongoBrasQuery, PostgresBrasQuery,
    CachingQuery, MongoCachingQuery, PostgresCachingQuery,
    RaiQuery, MongoRaiQuery, PostgresRaiQuery,
    TrafficHistoryQuery, MongoTrafficHistoryQuery, PostgresTrafficHistoryQuery
)
from model import TrafficHistoryModel
from handler import BordeHandler, BrasHandler, CachingHandler, RaiHandler
from utils.validate import Validate
from utils.log import log

class TrafficHandler:
    """Class to get history data."""

    __error_connection: bool = False
    __db_backup: bool = False
    traffic_query: TrafficHistoryQuery
    borde_query: BordeQuery
    bras_query: BrasQuery
    caching_query: CachingQuery
    rai_query: RaiQuery

    def __init__(self, db_backup: bool = False):
        try:
            if not db_backup: 
                self.traffic_query = MongoTrafficHistoryQuery()
                self.borde_query = MongoBordeQuery()
                self.bras_query = MongoBrasQuery()
                self.caching_query = MongoCachingQuery()
                self.rai_query = MongoRaiQuery()
            else: 
                self.__db_backup = True
                self.traffic_query = PostgresTrafficHistoryQuery()
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
                HeaderDataFrame.TIME,
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
            df_traffic = df.copy()
            if not df_traffic.empty and layer_type == LayerType.BORDE:
                borde_handler = BordeHandler(db_backup=self.__db_backup)
                df_layer = borde_handler.get_all_interfaces()
            elif not df_traffic.empty and layer_type == LayerType.BRAS:
                bras_handler = BrasHandler(db_backup=self.__db_backup)
                df_layer = bras_handler.get_all_interfaces()
            elif not df_traffic.empty and layer_type == LayerType.CACHING:
                caching_handler = CachingHandler(db_backup=self.__db_backup)
                df_layer = caching_handler.get_all_interfaces()
            elif not df_traffic.empty and layer_type == LayerType.RAI:
                rai_handler = RaiHandler(db_backup=self.__db_backup)
                df_layer = rai_handler.get_all_interfaces()
            elif not df_traffic.empty: raise Exception(f"Layer handler not found: {layer_type}")
            if df_layer.empty: raise Exception(f"Data of layer not found: {layer_type}")
            df_traffic.rename(columns={HeaderDataFrame.ID_LAYER: HeaderDataFrame.ID}, inplace=True)
            df_traffic = df_traffic.merge(df_layer, how="inner", on=HeaderDataFrame.ID)
            df_traffic = self.__format_layer_traffic(data=df_traffic)
            return df_traffic
        except Exception as e:
            log.error(f"Traffic handler. Failed to insert name layer in dataframe. {e}")
            return pd.DataFrame()

        
    def get_traffic_layer_by_days_before(self, layer_type: str, day_before: int = 30) -> pd.DataFrame:
        """Get all traffic history of a layer by dates before to today.

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
            df_traffic = pd.DataFrame()
            dates = [(date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(day_before)]
            df = pd.DataFrame()
            for date in dates:
                traffic: List[TrafficHistoryModel] = self.traffic_query.get_traffic_layer_by_date(layer_type=layer_type, date=date)
                if df.empty: df = pd.DataFrame([data.model_dump() for data in traffic])
                else: df = pd.concat([df, pd.DataFrame([data.model_dump() for data in traffic])])
            if not df.empty:
                df = self.__insert_name_layer(df=df, layer_type=layer_type)
                if not df_traffic.empty: df_traffic = pd.concat([df_traffic, df])
                else: df_traffic = df
            df_traffic = df_traffic.reset_index(drop=True)
            return df_traffic
        except Exception as e:
            log.error(f"Traffic handler. Failed to get traffic layer by days before. {e}")
            return pd.DataFrame()