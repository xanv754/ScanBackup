import os
import pandas as pd
from typing import List
from multiprocessing import Process
from constants.group import ModelBordeType, LayerType
from constants.path import DataPath
from constants.header import HeaderDataFrame, header_report_dialy
from datetime import datetime, timedelta
from database import MongoDailyReportQuery, PostgresDailyReportQuery
from handler import TrafficHandler, LayerHandler
from updater.update import UpdaterHandler
from utils.log import log


class DailyReportUpdaterHandler(UpdaterHandler):
    """Daily report data updater handler."""

    def _load_database(self, data: List[pd.DataFrame], db_backup: bool = False) -> bool:
        """Load the data obtained in the database."""
        failed = False
        layer_handler = LayerHandler(db_backup=db_backup)
        try:
            if db_backup: database = PostgresDailyReportQuery()
            else: database = MongoDailyReportQuery()
            for df in data:
                try:
                    layer_type = df[HeaderDataFrame.TYPE_LAYER][0]
                    df = df.drop(columns=[HeaderDataFrame.CAPACITY])
                    df_interfaces = layer_handler.get_all_interfaces(layer_type=layer_type)
                    if df_interfaces.empty: raise Exception(f"Data of layer not found: {layer_type}")
                    df = df.merge(df_interfaces, how="inner", on=[HeaderDataFrame.INTERFACE, HeaderDataFrame.TYPE])
                    df = df.drop(columns=[HeaderDataFrame.INTERFACE, HeaderDataFrame.TYPE, HeaderDataFrame.CAPACITY])
                    status_insert = database.new_report(data=df)
                    if not status_insert: raise Exception(f"Failed to insert daily report of {layer_type} into database.")
                except Exception as e:
                    log.error(f"Failed to load data of daily report. {e}")
                    continue
        except Exception as e:
            log.error(f"Failed to load data of daily report. {e}")
            failed = True
        return not failed

    def get_data(self, filepath: str | None = None, date: str | None = None) -> List[pd.DataFrame]:
        try:
            if not filepath: filepath = DataPath.SCAN_REPORT_DIALY
            if not os.path.exists(filepath) or not os.path.isdir(filepath):
                raise FileNotFoundError("Daily report folder not found.")
            datas = List[pd.DataFrame] = []
            files = [filename for filename in os.listdir(filepath)]
            for filename in files:
                try:
                    layer = filename.split("_")[1].upper()
                    df = pd.read_csv(filename, sep=" ", names=header_report_dialy, index_col=False)
                    if date: df = df[df[HeaderDataFrame.DATE] == date]
                    df[HeaderDataFrame.TYPE_LAYER] = layer
                    datas.append(df)
                except Exception as e:
                    log.error(f"Something went wrong to load data: {filename}. {e}")
                    continue
        except Exception as e:
            log.error(f"Failed to get data of daily report. {e}")
            return []
        else:
            return datas
        
    def load_data(self, data: List[pd.DataFrame], mongo: bool = False, postgres: bool = False) -> bool:
        try:
            load_mongo = Process(target=self._load_database, args=(data,))
            # load_postgres = Process(target=self._load_database, args=(data, True))
            load_mongo.start()
            # load_postgres.start()
            load_mongo.join()
            # load_postgres.join()
        except Exception as e:
            log.error(f"Failed to load data of daily report. {e}")
            return False
        else:
            return True