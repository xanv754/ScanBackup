import pandas as pd
from constants import header_bbip
from database import BBIPQuery, CachingMongoQuery
from utils.log import log


class CachingHandler:
    """Class to get data of caching layer."""

    __error_connection: bool = False
    caching_query: BBIPQuery

    def __init__(self, uri: str | None = None):
        try:
            self.caching_query = CachingMongoQuery(uri=uri)
        except Exception as e:
            log.error(f"Caching handler. Failed connecting to the database. {e}")
            self.__error_connection = True

    def get_all_interfaces(self) -> pd.DataFrame:
        """Get all interfaces of caching layer."""
        try:
            if self.__error_connection: 
                raise Exception("An error occurred while connecting to the database. The method has skipped.")
            df_interfaces = self.caching_query.get_interfaces()
        except Exception as e:
            log.error(f"Caching handler. Failed to get all interfaces of caching layer. {e}")
            return pd.DataFrame(columns=header_bbip)
        else:
            return df_interfaces