import pandas as pd
from constants.header import HeaderBordeDataFrameConstant
from database.querys.borde.borde import BordeQuery
from database.querys.borde.mongo import MongoBordeQuery
# from database.querys.borde.postgres import PostgresBordeQuery
from utils.log import log


class BordeHandler:
    """Class to get data of borde layer."""

    __error_connection: bool = False
    borde_query: BordeQuery

    def __init__(self, db_backup: bool = False):
        try:
            if not db_backup: 
                self.borde_query = MongoBordeQuery()
            # else: 
            #     self.borde_query = PostgresBordeQuery()
        except Exception as e:
            log.error(f"Borde handler. Failed connecting to the database. {e}")
            self.__error_connection = True

    def get_all_interfaces(self) -> pd.DataFrame:
        """Get all interfaces of borde layer."""
        try:
            if self.__error_connection: raise Exception("An error occurred while connecting to the database. The method has skipped.")
            interfaces = self.borde_query.get_interfaces()
            df = pd.DataFrame([data.model_dump(exclude={HeaderBordeDataFrameConstant.CREATE_AT}) for data in interfaces])
        except Exception as e:
            log.error(f"Borde handler. Failed to get all interfaces of borde layer. {e}")
            return pd.DataFrame()
        else:
            return df