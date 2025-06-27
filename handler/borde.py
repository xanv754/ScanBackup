import pandas as pd
from constants.header import HeaderDataFrame
from database import BordeQuery, BordeMongoQuery, PostgresBordeQuery
from utils.log import log


class BordeHandler:
    """Class to get data of borde layer."""

    __error_connection: bool = False
    borde_query: BordeQuery

    def __init__(self, db_backup: bool = False, uri: str | None = None):
        try:
            if not db_backup: self.borde_query = BordeMongoQuery(uri=uri)
            else: self.borde_query = PostgresBordeQuery(uri=uri)
        except Exception as e:
            log.error(f"Borde handler. Failed connecting to the database. {e}")
            self.__error_connection = True

    def get_all_interfaces(self) -> pd.DataFrame:
        """Get all interfaces of borde layer."""
        try:
            if self.__error_connection: raise Exception("An error occurred while connecting to the database. The method has skipped.")
            df_interfaces = self.borde_query.get_interfaces()
            df_interfaces.drop(columns=[HeaderDataFrame.CREATE_AT], inplace=True)
        except Exception as e:
            log.error(f"Borde handler. Failed to get all interfaces of borde layer. {e}")
            return pd.DataFrame()
        else:
            return df_interfaces