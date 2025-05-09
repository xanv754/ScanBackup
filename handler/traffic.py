import pandas as pd
from typing import List
from datetime import datetime, timedelta
from constants.group import LayerType
from constants.header import HeaderTrafficDataFrameConstant, HeaderBordeDataFrameConstant, HeaderBrasDataFrameConstant, HeaderCachingDataFrameConstant, HeaderRaiDataFrameConstant
from model.trafficHistory import TrafficHistoryModel
from database.querys.borde.borde import BordeQuery
from database.querys.borde.mongo import MongoBordeQuery
from database.querys.borde.postgres import PostgresBordeQuery
from database.querys.bras.bras import BrasQuery
from database.querys.bras.mongo import MongoBrasQuery
from database.querys.bras.postgres import PostgresBrasQuery
from database.querys.caching.caching import CachingQuery
from database.querys.caching.mongo import MongoCachingQuery
from database.querys.caching.postgres import PostgresCachingQuery
from database.querys.rai.rai import RaiQuery
from database.querys.rai.mongo import MongoRaiQuery
from database.querys.rai.postgres import PostgresRaiQuery
from database.querys.traffic.traffic import TrafficHistoryQuery
from database.querys.traffic.mongo import MongoTrafficHistoryQuery
from database.querys.traffic.postgres import PostgresTrafficHistoryQuery
from handler.borde import BordeHandler
from handler.bras import BrasHandler
from handler.caching import CachingHandler
from handler.rai import RaiHandler
from utils.validate import Validate
from utils.log import log

class TrafficHandler:
    """Class to get history data."""

    __error_connection: bool = False
    traffic_query: TrafficHistoryQuery
    borde_query: BordeQuery
    bras_query: BrasQuery
    caching_query: CachingQuery
    rai_query: RaiQuery

    def __init__(self, db_backup: bool = False):
        try:
            if not hasattr(self, "__initialized"):
                self.__initialized = True
                if not db_backup: 
                    self.traffic_query = MongoTrafficHistoryQuery()
                    self.borde_query = MongoBordeQuery()
                    self.bras_query = MongoBrasQuery()
                    self.caching_query = MongoCachingQuery()
                    self.rai_query = MongoRaiQuery()
                else: 
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
            df.drop(columns=[HeaderTrafficDataFrameConstant.TYPE_LAYER], inplace=True)
            df = df.reindex([
                HeaderTrafficDataFrameConstant.NAME, 
                HeaderTrafficDataFrameConstant.CAPACITY,
                HeaderTrafficDataFrameConstant.DATE, 
                HeaderTrafficDataFrameConstant.TIME, 
                HeaderTrafficDataFrameConstant.IN_PROM, 
                HeaderTrafficDataFrameConstant.OUT_PROM, 
                HeaderTrafficDataFrameConstant.IN_MAX, 
                HeaderTrafficDataFrameConstant.OUT_MAX
            ], axis="columns")
            return df
        except Exception as e:
            log.error(f"Traffic handler. Failed to format dataframe. {e}")
            return data
        
    def __format_borde_traffic(self, data: pd.DataFrame) -> pd.DataFrame:
        """Format a dataframe of data traffic history with data borde."""
        try:
            df = data.copy()
            df.drop(columns=[
                HeaderBordeDataFrameConstant.ID,
                HeaderBordeDataFrameConstant.MODEL,
            ], inplace=True)
            df.rename(columns={
                HeaderBordeDataFrameConstant.NAME: HeaderTrafficDataFrameConstant.NAME,
                HeaderBordeDataFrameConstant.CAPACITY: HeaderTrafficDataFrameConstant.CAPACITY,
            }, inplace=True)
            df = self.__format_traffic(data=df)
            return df
        except Exception as e:
            log.error(f"Traffic handler. Failed to format dataframe. {e}")
            return data
        
    def __format_bras_traffic(self, data: pd.DataFrame) -> pd.DataFrame:
        """Format a dataframe of data traffic history with data bras."""
        try:
            df = data.copy()
            df.drop(columns=[HeaderBrasDataFrameConstant.ID, HeaderBrasDataFrameConstant.TYPE], inplace=True)
            df = df.reindex([
                HeaderBrasDataFrameConstant.NAME, 
                HeaderBrasDataFrameConstant.TYPE, 
                HeaderBrasDataFrameConstant.CAPACITY, 
                HeaderTrafficDataFrameConstant.DATE, 
                HeaderTrafficDataFrameConstant.TIME, 
                HeaderTrafficDataFrameConstant.IN_PROM, 
                HeaderTrafficDataFrameConstant.OUT_PROM, 
                HeaderTrafficDataFrameConstant.IN_MAX, 
                HeaderTrafficDataFrameConstant.OUT_MAX
            ], axis="columns")
            df.rename(columns={
                HeaderBrasDataFrameConstant.NAME: HeaderTrafficDataFrameConstant.NAME,
                HeaderBrasDataFrameConstant.CAPACITY: HeaderTrafficDataFrameConstant.CAPACITY,
            }, inplace=True)
            return df
        except Exception as e:
            log.error(f"Traffic handler. Failed to format dataframe. {e}")
            return data
        
    def __format_caching_traffic(self, data: pd.DataFrame) -> pd.DataFrame:
        """Format a dataframe of data traffic history with data caching."""
        try:
            df = data.copy()
            df.drop(columns=[HeaderCachingDataFrameConstant.ID, HeaderCachingDataFrameConstant.SERVICE], inplace=True)
            df.rename(columns={
                HeaderCachingDataFrameConstant.NAME: HeaderTrafficDataFrameConstant.NAME,
                HeaderCachingDataFrameConstant.CAPACITY: HeaderTrafficDataFrameConstant.CAPACITY,
            }, inplace=True)
            df = self.__format_traffic(data=df)
            return df
        except Exception as e:
            log.error(f"Traffic handler. Failed to format dataframe. {e}")
            return data
        
    def __format_rai_traffic(self, data: pd.DataFrame) -> pd.DataFrame:
        """Format a dataframe of data traffic history with data rai."""
        try:
            df = data.copy()
            df.drop(columns=[HeaderRaiDataFrameConstant.ID], inplace=True)
            df = self.__format_traffic(data=df)
            df.rename(columns={
                HeaderRaiDataFrameConstant.NAME: HeaderTrafficDataFrameConstant.NAME,
                HeaderRaiDataFrameConstant.CAPACITY: HeaderTrafficDataFrameConstant.CAPACITY,
            }, inplace=True)
            return df
        except Exception as e:
            log.error(f"Traffic handler. Failed to format dataframe. {e}")
            return data
        
    def __insert_name_layer(self, df_traffic: pd.DataFrame, layer_type: str) -> pd.DataFrame:
        """Insert interface name each interface of a layer in a dataframe."""
        try:
            df = df_traffic.copy()
            if not df.empty and layer_type == LayerType.BORDE:
                borde_handler = BordeHandler()
                df_borde = borde_handler.get_all_interfaces()
                df.rename(columns={HeaderTrafficDataFrameConstant.ID_LAYER: HeaderBordeDataFrameConstant.ID}, inplace=True)
                df = df.merge(df_borde, how="inner", on=HeaderBordeDataFrameConstant.ID)
                df = self.__format_borde_traffic(data=df)
            elif not df.empty and layer_type == LayerType.BRAS:
                bras_handler = BrasHandler()
                df_bras = bras_handler.get_all_interfaces()
                df.rename(columns={HeaderTrafficDataFrameConstant.ID_LAYER: HeaderBrasDataFrameConstant.ID}, inplace=True)
                df = df.merge(df_bras, how="inner", on=HeaderBrasDataFrameConstant.ID)
                df = self.__format_bras_traffic(data=df)
            elif not df.empty and layer_type == LayerType.CACHING:
                caching_handler = CachingHandler()
                df_caching = caching_handler.get_all_interfaces()
                df.rename(columns={HeaderTrafficDataFrameConstant.ID_LAYER: HeaderCachingDataFrameConstant.ID}, inplace=True)
                df = df.merge(df_caching, how="inner", on=HeaderCachingDataFrameConstant.ID)
                df = self.__format_caching_traffic(data=df)
            elif not df.empty and layer_type == LayerType.RAI:
                rai_handler = RaiHandler()
                df_rai = rai_handler.get_all_interfaces()
                df.rename(columns={HeaderTrafficDataFrameConstant.ID_LAYER: HeaderRaiDataFrameConstant.ID}, inplace=True)
                df = df.merge(df_rai, how="inner", on=HeaderRaiDataFrameConstant.ID)
                df = self.__format_rai_traffic(data=df)
            elif not df.empty:
                raise Exception(f"Layer handler not found: {layer_type}")
        except Exception as e:
            log.error(f"Traffic handler. Failed to insert name layer in dataframe. {e}")
            return pd.DataFrame()
        else:
            return df
    
    def get_traffic_interface_by_date(self, layer_type: str, interface_name: str, date: str = datetime.now().strftime("%Y-%m-%d")) -> pd.DataFrame:
        """Get all traffic history of a interface of a layer by a date.

        Parameters
        ----------
        layer_type : str
            Type name of the layer to consult.
        interface_name : str
            Name of the interface to consult.
        date : str, default today
            Date of traffic history to consult. Format YYYY-MM-DD.
        """
        try:
            if self.__error_connection: raise Exception("An error occurred while connecting to the database. The method has skipped.")
            if not Validate.layer_type(layer_type):
                raise Exception("Invalid parameter: name layer.")
            if not Validate.date(date):
                raise Exception("Invalid parameter: date.")
            if layer_type == LayerType.BORDE:
                interface = self.borde_query.get_interface(name=interface_name)
            elif layer_type == LayerType.BRAS:
                interface = self.bras_query.get_bras(brasname=interface_name, type=LayerType.BRAS)
            elif layer_type == LayerType.CACHING:
                interface = self.caching_query.get_interface(name=interface_name)
            else:
                interface = self.rai_query.get_interface(name=interface_name)
            if not interface:
                raise Exception(f"Requested interface ({interface_name}) not found in database.")
            traffic = self.traffic_query.get_traffic_interface_by_date(id=interface.id, date=date)
            df = pd.DataFrame([data.model_dump(exclude={HeaderTrafficDataFrameConstant.ID_LAYER}) for data in traffic])
            df[HeaderTrafficDataFrameConstant.NAME] = interface_name
            df[HeaderTrafficDataFrameConstant.CAPACITY] = interface.capacity
            df = self.__format_traffic(data=df)
        except Exception as e:
            log.error(f"Traffic handler. Failed to get traffic of layer by a date. {e}")
            return pd.DataFrame()
        else:
            return df
        
    def get_traffic_layer_by_thirty_days_before(self, layer_type: str, date: str = datetime.now().strftime("%Y-%m-%d")) -> pd.DataFrame:
        """Get all traffic history of a layer by a date.

        Parameters
        ----------
        layer_type : str
            Type name of the layer to consult.
        date : str, default today
            Date of traffic history to consult. Format YYYY-MM-DD.
        """
        try:
            if self.__error_connection: raise Exception("An error occurred while connecting to the database. The method has skipped.")
            if not Validate.layer_type(layer_type):
                raise Exception("Invalid parameter: name layer.")
            if not Validate.date(date):
                raise Exception("Invalid parameter: date.")
            df_traffic = pd.DataFrame()
            date = datetime.strptime(date, "%Y-%m-%d")
            dates = [(date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30)]
            for date in dates:
                traffic: List[TrafficHistoryModel] = self.traffic_query.get_traffic_layer_by_date(layer_type=layer_type, date=date)
                df = pd.DataFrame([data.model_dump() for data in traffic])
                if not df.empty:
                    df = self.__insert_name_layer(df_traffic=df, layer_type=layer_type)
                    if not df_traffic.empty:
                        df_traffic = pd.concat([df_traffic, df])
                    else:
                        df_traffic = df
            df_traffic = df_traffic.reset_index(drop=True)
            return df_traffic
        except Exception as e:
            log.error(f"Traffic handler. Failed to get traffic of layer by a date. {e}")
            return pd.DataFrame()