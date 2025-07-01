import os
import pandas as pd
from datetime import datetime, timedelta
from typing import List
from constants import DataPath, HeaderDailyReport, header_daily_report, header_upload_daily_data
from database import DailyReportMongoQuery
from model import DailyReportModel
from updater.update import UpdaterHandler
from utils.log import log


class DailyReportUpdaterHandler(UpdaterHandler):
    """Daily report data updater handler."""

    def get_data(self, folderpath: str | None = None, date: str | None = None) -> pd.DataFrame:
        try:
            if not folderpath: folderpath = DataPath.SCAN_REPORT_DAILY
            if not os.path.exists(folderpath) or not os.path.isdir(folderpath):
                raise FileNotFoundError("Daily report folder not found.")
            if not date: date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            df_data = pd.DataFrame(columns=header_daily_report)
            files = [filename for filename in os.listdir(folderpath)]
            for filename in files:
                try:
                    layer = filename.replace(".", "_").split("_")[1].upper().strip()
                    df = pd.read_csv(f"{folderpath}/{filename}", sep=" ", names=header_upload_daily_data, index_col=False, skiprows=1)
                    df = df[df[HeaderDailyReport.DATE] == date]
                    if not df.empty:
                        df[HeaderDailyReport.TYPE_LAYER] = layer
                        if df_data.empty: df_data = df
                        else: df_data = pd.concat([df_data, df], axis=0)
                except Exception as e:
                    log.error(f"Something went wrong to get data: {filename}. {e}")
                    continue
        except Exception as e:
            log.error(f"Failed to get data of daily report. {e}")
            return pd.DataFrame(columns=header_daily_report)
        else:
            return df_data
        
    def load_data(self, data: pd.DataFrame, uri: str | None = None) -> bool:
        try:
            if data.empty: 
                log.warning("The system received empty data daily report whten it updated.")
                return True
            query = DailyReportMongoQuery(uri=uri)
            data_json = data.to_dict(orient="records")
            try:
                json = [DailyReportModel(**item) for item in data_json]
            except Exception as e:
                log.error(f"Failed to validate data with the model. Daily report updater system has suspended. {e}")
                return False
            else:
                response = query.new_report(json)
                return response
        except Exception as e:
            log.error(f"Failed to load data of daily report. {e}")
            return False