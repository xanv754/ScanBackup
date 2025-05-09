import pandas as pd
from constants.header import HeaderBrasDataFrameConstant
from database.querys.bras.bras import BrasQuery
from database.querys.bras.mongo import MongoBrasQuery
from database.querys.bras.postgres import PostgresBrasQuery
from utils.log import log


class BrasHandler:
    """Class to get data of bras layer."""
    __error_connection: bool = False
    bras_query: BrasQuery

    def __init__(self, db_backup: bool = False):
        try:
            if not hasattr(self, "__initialized"):
                self.__initialized = True
                if not db_backup: 
                    self.bras_query = MongoBrasQuery()
                else: 
                    self.bras_query = PostgresBrasQuery()
        except Exception as e:
            log.export(f"Bras handler. Failed connecting to the database. {e}")
            self.__error_connection = True

    def get_all_interfaces(self) -> pd.DataFrame:
        """Get all interfaces of bras layer."""
        try:
            if self.__error_connection: raise Exception("An error occurred while connecting to the database. The method has skipped.")
            interfaces = self.bras_query.get_all_bras()
            df = pd.DataFrame([data.model_dump(exclude={HeaderBrasDataFrameConstant.CREATE_AT}) for data in interfaces])
        except Exception as e:
            log.export(f"Bras handler. Failed to get all interfaces of bras layer. {e}")
            return pd.DataFrame()
        else:
            return df