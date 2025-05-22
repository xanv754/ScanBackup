import pandas as pd
from constants.header import HeaderDataFrame
from database import RaiQuery, MongoRaiQuery, PostgresRaiQuery
from utils.log import log


class RaiHandler:
    """Class to get data of rai layer."""

    __error_connection: bool = False
    rai_query: RaiQuery

    def __init__(self, db_backup: bool = False):
        try:
            if not db_backup: 
                self.rai_query = MongoRaiQuery()
            else: self.rai_query = PostgresRaiQuery()
        except Exception as e:
            log.error(f"Rai handler. Failed connecting to the database. {e}")
            self.__error_connection = True

    def get_all_interfaces(self) -> pd.DataFrame:
        """Get all interfaces of rai layer."""
        try:
            if self.__error_connection: raise Exception("An error occurred while connecting to the database. The method has skipped.")
            df_interfaces = self.rai_query.get_interfaces()
            df_interfaces.drop(columns=[HeaderDataFrame.CREATE_AT], inplace=True)
        except Exception as e:
            log.error(f"rai handler. Failed to get all interfaces of rai layer. {e}")
            return pd.DataFrame()
        else:
            return df_interfaces