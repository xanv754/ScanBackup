import pandas as pd
from multiprocessing import Process
from datetime import datetime, timedelta
from database import MongoDailyReportQuery, PostgresDailyReportQuery
from handler import TrafficHandler
from utils.log import log


class DailyReportUpdaterHandler():
    """Daily report data updater handler."""
    
    def __calculate_last_data(self, layer_type: str, date: str | None = None, db_backup: bool = False) -> pd.DataFrame:
        """Generate the values of daily report to last traffic history.
        
        Parameters
        ----------
        layer_type : str
            Type name of the layer to consult.
        """
        if not date:
            date = datetime.now() - timedelta(days=1)
            date = date.strftime("%Y-%m-%d")
        traffic = TrafficHandler(db_backup=db_backup)
        data = traffic.get_traffic_layer_by_day(layer_type=layer_type, date=date)

        # TODO: Calculate prom and max prom (df_calculate)

        df_calculate: pd.DataFrame
        return df_calculate

    def __load_database(self, data: pd.DataFrame, db_backup: bool = False) -> bool:
        """Load the data obtained in the database."""
        failed = False
        try:
            if db_backup: database = PostgresDailyReportQuery()
            else: database = MongoDailyReportQuery()
            database.new_report(data=data)
        except Exception as e:
            log.error(f"Failed to insert a daily report. {e}")
            failed = True
        return not failed
    
    def generate_report(self, layer_type: str, date: str | None = None, db_backup: bool = False) -> bool:
        """Generate a daily report of a layer.

        Parameters
        ----------
        layer_type : str
            Type name of the layer to consult.
        """
        try:
            data = self.__calculate_last_data(layer_type=layer_type, date=date, db_backup=db_backup)
            load_mongo = Process(target=self.__load_database, args=(data,))
            load_postgres = Process(target=self.__load_database, args=(data, True))
            load_mongo.start()
            load_postgres.start()
            load_mongo.join()
            load_postgres.join()
        except Exception as e:
            log.error(f"Failed to generate daily report of {layer_type}. {e}")
            return False
        else:
            return True