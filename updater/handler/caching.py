import os
import pandas as pd
from datetime import datetime, timedelta
from constants import DataPath, HeaderBBIP, header_bbip, header_upload_scan_data
from database import CachingMongoQuery
from model import BBIPModel
from updater.update import UpdaterHandler
from utils.log import log


class CachingUpdaterHandler(UpdaterHandler):
    """Caching data updater handler."""

    def get_data(self, folderpath: str | None = None, date: str | None = None, force: bool = False) -> pd.DataFrame:
        try:
            if not folderpath: folderpath = DataPath.SCAN_DATA_CACHING
            if not os.path.exists(folderpath) or not os.path.isdir(folderpath):
                raise FileNotFoundError("Caching folder not found.")
            if not date: date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            files = [filename for filename in os.listdir(folderpath)]
            df_to_upload = pd.DataFrame(columns=header_bbip)
            for filename in files:
                try:
                    type = filename.split("%")[0]
                    interface = filename.split("%")[1]
                    capacity = filename.split("%")[2]
                    df_data = pd.read_csv(f"{folderpath}/{filename}", sep=" ", header=None, names=header_upload_scan_data)
                    if not force: df_data = df_data[df_data[HeaderBBIP.DATE] == date]
                    if not df_data.empty:
                        df_data[HeaderBBIP.NAME] = interface
                        df_data[HeaderBBIP.CAPACITY] = capacity
                        df_data[HeaderBBIP.TYPE] = type
                        if df_to_upload.empty: df_to_upload = df_data
                        else: df_to_upload = pd.concat([df_to_upload, df_data], axis=0)
                except Exception as e:
                    log.error(f"Something went wrong to load data: {filename}. {e}")
                    continue                    
        except Exception as e:
            log.error(f"Failed to data load of Caching layer. {e}")
            return pd.DataFrame(columns=header_bbip)
        else:
            return df_to_upload

    def load_data(self, data: pd.DataFrame, uri: str | None = None) -> bool:
        try:
            if data.empty: 
                log.warning("The system received empty data Caching when it updated.")
                return False
            query = CachingMongoQuery(uri=uri)
            data_json = data.to_dict(orient="records")
            try:
                json = [BBIPModel(**item) for item in data_json]
            except Exception as e:
                log.error(f"Failed to validate data with the model. Caching updater system has suspended. {e}")
                return False
            else:
                response = query.new_interface(json)
                return response
        except Exception as e:
            log.error(f"Failed to load data of Caching layer. {e}")
            return False
