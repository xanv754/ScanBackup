import pandas as pd
from constants.header import HeaderDataFrame
from constants.group import LayerType
from database import (
    BordeQuery, MongoBordeQuery, PostgresBordeQuery,
    BrasQuery, MongoBrasQuery, PostgresBrasQuery,
    CachingQuery, MongoCachingQuery, PostgresCachingQuery,
    RaiQuery, MongoRaiQuery, PostgresRaiQuery
)
from utils.validate import Validate
from utils.log import log


class LayerHandler:
    """Class to get data of borde layer."""

    __error_connection: bool = False
    borde_query: BordeQuery
    bras_query: BrasQuery
    caching_query: CachingQuery
    rai_query: RaiQuery

    def __init__(self, db_backup: bool = False):
        try:
            if not db_backup: 
                self.borde_query = MongoBordeQuery()
                self.bras_query = MongoBrasQuery()
                self.caching_query = MongoCachingQuery()
                self.rai_query = MongoRaiQuery()
            else: 
                self.borde_query = PostgresBordeQuery()
                self.bras_query = PostgresBrasQuery()
                self.caching_query = PostgresCachingQuery()
                self.rai_query = PostgresRaiQuery()
        except Exception as e:
            log.error(f"Borde handler. Failed connecting to the database. {e}")
            self.__error_connection = True

    def get_all_interfaces(self, layer_type: str) -> pd.DataFrame:
        """Get all interfaces of a layer."""
        try:
            if self.__error_connection: raise Exception("An error occurred while connecting to the database. The method has skipped.")
            if not Validate.layer_type(layer_type): raise Exception("Invalid parameter: type layer.")
            if layer_type == LayerType.BORDE:
                df_interfaces = self.borde_query.get_interfaces()
                df_interfaces.drop(columns=[HeaderDataFrame.CREATE_AT], inplace=True)
            elif layer_type == LayerType.BRAS:
                df_interfaces = self.bras_query.get_interfaces()
                df_interfaces.drop(columns=[HeaderDataFrame.CREATE_AT], inplace=True)
            elif layer_type == LayerType.CACHING:
                df_interfaces = self.caching_query.get_interfaces()
                df_interfaces.drop(columns=[HeaderDataFrame.CREATE_AT], inplace=True)
            elif layer_type == LayerType.RAI:
                df_interfaces = self.rai_query.get_interfaces()
                df_interfaces.drop(columns=[HeaderDataFrame.CREATE_AT], inplace=True)
            else: raise Exception(f"Layer handler not found: {layer_type}")
        except Exception as e:
            log.error(f"Borde handler. Failed to get all interfaces of borde layer. {e}")
            return pd.DataFrame()
        else:
            return df_interfaces