import ast
import json
import pandas as pd
from typing import List
from constants.header import HeaderConstants
from updater.update import UpdaterHandler
from utils.log import LogHandler


class HistoryUpdaterHandler(UpdaterHandler):
    """Class to get history data of files."""

    def get_data(self, filepath: str | None = None) -> List:
        try:
            if filepath:
                new_header = [
                    HeaderConstants.DATE,
                    HeaderConstants.TIME,
                    HeaderConstants.IN_PROM,
                    HeaderConstants.OUT_PROM,
                    HeaderConstants.IN_MAX,
                    HeaderConstants.OUT_MAX
                ]
                df = pd.read_csv(filepath, header=0)
                df.columns = new_header
                data_str = df.to_json(orient='records')
                if data_str:
                    parsed = json.loads(data_str)
                    data_json = json.dumps(parsed, indent=4)
                    data_json = ast.literal_eval(data_str)
                    return data_json
            return []
        except Exception as e:
            print(f"Failed to obtain history data. {e}")
            return []
