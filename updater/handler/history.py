import ast
import json
import pandas as pd
from typing import List, Tuple
from model.trafficHistory import TrafficHistoryModel
from updater.update import UpdaterHandler
from storage.constant.fields import TrafficHistoryFieldDatabase
from storage.querys.history.mongo import MongoHistoryTrafficQuery
from utils.log import LogHandler


class HistoryUpdaterHandler(UpdaterHandler):
    """Class to get history data of files."""

    def get_data(self, filepath: str | None = None) -> List[TrafficHistoryModel]:
        try:
            if filepath:
                traffic: List[TrafficHistoryModel] = []
                with open(filepath, "r") as file:
                    lines = file.readlines()
                    for line in lines[1:]:
                        new_traffic = TrafficHistoryModel(
                            date=line.split(" ")[0],
                            time=line.split(" ")[1],
                            idLayer="",
                            typeLayer="",
                            inProm=int(line.split(" ")[2]),
                            outProm=int(line.split(" ")[3]),
                            inMax=int(line.split(" ")[4]),
                            outMax=int(line.split(" ")[5]),
                        )
                        traffic.append(new_traffic)
                return traffic
            return []
        except Exception as e:
            LogHandler.log(f"Failed to get data of history traffic. {e}", err=True)
            return []
        
    def load_data(self, data: List[TrafficHistoryModel]) -> bool:
        try:
            database = MongoHistoryTrafficQuery()
            response = database.new_histories(new_histories=data)
        except Exception as e:
            LogHandler.log(f"Failed to load data of history traffic. {e}", err=True)
            return False
        else:
            return response