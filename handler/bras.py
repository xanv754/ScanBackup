import pandas as pd
from constants import header_bbip
from database import BBIPQuery, BrasMongoQuery
from utils.log import log


class BrasHandler:
    """Class to get data of bras layer."""
    __error_connection: bool = False
    bras_query: BBIPQuery

    def __init__(self, uri: str | None = None):
        try:
            self.bras_query = BrasMongoQuery(uri=uri)
        except Exception as e:
            log.export(f"Bras handler. Failed connecting to the database. {e}")
            self.__error_connection = True

    def get_all_interfaces(self) -> pd.DataFrame:
        """Get all interfaces of bras layer."""
        try:
            if self.__error_connection: 
                raise Exception("An error occurred while connecting to the database. The method has skipped.")
            df_interfaces = self.bras_query.get_interfaces()
        except Exception as e:
            log.export(f"Bras handler. Failed to get all interfaces of bras layer. {e}")
            return pd.DataFrame(columns=header_bbip)
        else:
            return df_interfaces