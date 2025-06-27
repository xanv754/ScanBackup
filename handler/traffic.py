import pandas as pd
from datetime import datetime, timedelta
from constants.header import HeaderDataFrame
from database import TrafficHistoryQuery, MongoTrafficHistoryQuery, PostgresTrafficHistoryQuery
from handler import BBIPHandler
from utils.validate import Validate
from utils.log import log

class TrafficHandler:
    """Class to get history data."""

    __error_connection: bool = False
    __db_backup: bool = False
    traffic_query: TrafficHistoryQuery

    def __init__(self, db_backup: bool = False, uri: str | None = None):
        try:
            self.__db_backup = db_backup
            if not db_backup: self.traffic_query = MongoTrafficHistoryQuery(uri=uri)
            else: self.traffic_query = PostgresTrafficHistoryQuery(uri=uri)
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
            if not df_traffic.empty:
                layer_handler = BBIPHandler(db_backup=self.__db_backup)
                df_layer = layer_handler.get_all_interfaces(layer_type=layer_type)
            if df_layer.empty: raise Exception(f"Data of layer not found: {layer_type}")
            df_traffic.rename(columns={HeaderDataFrame.ID_LAYER: HeaderDataFrame.ID}, inplace=True)
            df_traffic = df_traffic.merge(df_layer, how="inner", on=HeaderDataFrame.ID)
            df_traffic = self.__format_layer_traffic(data=df_traffic)
            return df_traffic
        except Exception as e:
            log.error(f"Traffic handler. Failed to insert name layer in dataframe. {e}")
            return pd.DataFrame()

        
    def get_traffic_layer_by_days_ago(self, layer_type: str, day_before: int = 30) -> pd.DataFrame:
        """Get all traffic history of a layer by days before today.

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
                traffic = self.traffic_query.get_traffic_layer_by_date(layer_type=layer_type, date=date)
                traffic[HeaderDataFrame.ID_LAYER] = traffic[HeaderDataFrame.ID_LAYER].astype(str)
                if data.empty: data = traffic
                else: data = pd.concat([data, traffic])
            if not data.empty: data = self.__insert_name_layer(df=data, layer_type=layer_type)
            data = data.reset_index(drop=True)
            return data
        except Exception as e:
            log.error(f"Traffic handler. Failed to get traffic layer by days before. {e}")
            return pd.DataFrame()
        
    def get_traffic_layer_by_day(self, layer_type: str, date: str | None = None) -> pd.DataFrame:
        """Get all traffic history of a layer by a date.

        Parameters
        ----------
        layer_type : str
            Type name of the layer to consult.
        date: str, default None
            Date to get traffic history.
        """
        try:
            if self.__error_connection: raise Exception("An error occurred while connecting to the database. The method has skipped.")
            if not Validate.layer_type(layer_type): raise Exception("Invalid parameter: name layer.")
            if not date:
                date = datetime.now().date()
                date = date - timedelta(days=1)
            else:
                if not Validate.date(date): raise Exception("Invalid parameter: date.")
            traffic = self.traffic_query.get_traffic_layer_by_date(layer_type=layer_type, date=date)
            traffic[HeaderDataFrame.ID_LAYER] = traffic[HeaderDataFrame.ID_LAYER].astype(str)
            if not traffic.empty: traffic = self.__insert_name_layer(df=traffic, layer_type=layer_type)
            traffic = traffic.reset_index(drop=True)
            return traffic
        except Exception as e:
            log.error(f"Traffic handler. Failed to get traffic layer by a day. {e}")
            return pd.DataFrame()