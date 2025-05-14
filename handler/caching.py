import pandas as pd
from constants.header import HeaderDataFrame
from database import CachingQuery, MongoCachingQuery, PostgresCachingQuery
from utils.log import log


class CachingHandler:
    """Class to get data of caching layer."""

    __error_connection: bool = False
    caching_query: CachingQuery

    def __init__(self, db_backup: bool = False):
        try:
            if not db_backup: self.caching_query = MongoCachingQuery()
            else: self.caching_query = PostgresCachingQuery()
        except Exception as e:
            log.error(f"Caching handler. Failed connecting to the database. {e}")
            self.__error_connection = True

    def get_all_interfaces(self) -> pd.DataFrame:
        """Get all interfaces of caching layer."""
        try:
            if self.__error_connection: raise Exception("An error occurred while connecting to the database. The method has skipped.")
            interfaces = self.caching_query.get_interfaces()
            df = pd.DataFrame([data.model_dump(exclude={HeaderDataFrame.CREATE_AT}) for data in interfaces])
        except Exception as e:
            log.error(f"Caching handler. Failed to get all interfaces of caching layer. {e}")
            return pd.DataFrame()
        else:
            return df