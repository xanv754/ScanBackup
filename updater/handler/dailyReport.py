import os
import pandas as pd
from datetime import datetime, timedelta
from typing import List
from multiprocessing import Process
from constants.path import DataPath
from constants.header import HeaderDataFrame, header_report_dialy
from database import MongoDailyReportQuery, PostgresDailyReportQuery
from constants.group import LayerType
from handler import LayerHandler
from updater.update import UpdaterHandler
from utils.log import log


class DailyReportUpdaterHandler(UpdaterHandler):
    """Daily report data updater handler."""

    def _load_database(self, data: List[pd.DataFrame], db_backup: bool = False, uri: str | None = None) -> bool:
        """Load the data obtained in the database."""
        failed = False
        layer_handler = LayerHandler(db_backup=db_backup, uri=uri)
        try:
            if db_backup: database = PostgresDailyReportQuery(uri=uri)
            else: database = MongoDailyReportQuery(uri=uri)
            for df in data:
                try:
                    layer_type = df[HeaderDataFrame.TYPE_LAYER].iloc[0]
                    df = df.drop(columns=[HeaderDataFrame.CAPACITY])
                    df_interfaces = layer_handler.get_all_interfaces(layer_type=layer_type)
                    df_interfaces.rename(columns={
                        HeaderDataFrame.NAME: HeaderDataFrame.INTERFACE,
                        HeaderDataFrame.MODEL: HeaderDataFrame.TYPE,
                        HeaderDataFrame.SERVICE: HeaderDataFrame.TYPE
                    }, inplace=True)
                    if df_interfaces.empty: raise Exception(f"Data of layer not found: {layer_type}")
                    if layer_type == LayerType.RAI:
                        df = df.merge(df_interfaces, how="inner", on=[HeaderDataFrame.INTERFACE])
                    else:
                        df = df.merge(df_interfaces, how="inner", on=[HeaderDataFrame.INTERFACE, HeaderDataFrame.TYPE])
                    df = df.drop(columns=[HeaderDataFrame.INTERFACE, HeaderDataFrame.TYPE, HeaderDataFrame.CAPACITY])
                    df.rename(columns={
                        HeaderDataFrame.ID: HeaderDataFrame.ID_LAYER
                    }, inplace=True)
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
            if not date: 
                date = datetime.now() - timedelta(days=1)
                date = date.strftime("%Y-%m-%d")
            if not filepath: filepath = DataPath.SCAN_REPORT_DAILY
            if not os.path.exists(filepath) or not os.path.isdir(filepath):
                raise FileNotFoundError("Daily report folder not found.")
            datas: List[pd.DataFrame] = []
            files = [filename for filename in os.listdir(filepath)]
            for filename in files:
                try:
                    layer = filename.replace(".", "_").split("_")[1].upper().strip()
                    df = pd.read_csv(f"{filepath}/{filename}", sep=" ", names=header_report_dialy, index_col=False, skiprows=1)
                    df = df[df[HeaderDataFrame.DATE] == date]
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
        
    def load_data(self, data: List[pd.DataFrame]) -> bool:
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