import os
from typing import List, Tuple
from rich.progress import track
from constants.path import PathConstant
from model.rai import RaiModel
from model.trafficHistory import TrafficHistoryModel
from updater.update import UpdaterHandler
from updater.handler.history import HistoryUpdaterHandler
from storage.constant.tables import TableNameDatabase
from storage.querys.rai.mongo import MongoRaiQuery
from utils.log import LogHandler


class RaiUpdaterHandler(UpdaterHandler):
    """Rai data updater handler."""

    def get_data(self, filepath: str | None = None) -> List[Tuple[RaiModel, List[TrafficHistoryModel]]]:
        try:
            if not os.path.exists(PathConstant.SCAN_DATA_RAI) or not os.path.isdir(PathConstant.SCAN_DATA_RAI):
                raise FileNotFoundError("Rai folder not found.")
            files = [filename for filename in os.listdir(PathConstant.SCAN_DATA_RAI)]
            data: List[Tuple[RaiModel, List[TrafficHistoryModel]]] = []
            for filename in track(files, description="Reading data caching..."):
                try:
                    interface = filename.split("%")[0]
                    capacity = int(filename.split("%")[1])
                    interface_border = RaiModel(
                        interface=interface,
                        capacity=capacity
                    )
                    historyHandler = HistoryUpdaterHandler()
                    traffic_border = historyHandler.get_data(filepath=f"{PathConstant.SCAN_DATA_RAI}/{filename}")
                except Exception as e:
                    LogHandler.log(f"Something went wrong to load data: {filename}. {e}", err=True)
                    continue
                else:
                    data.append((interface_border, traffic_border))
        except Exception as e:
            LogHandler.log(f"Failed to data load of Caching layer. {e}", err=True)
            return []
        else:
            return data

    def load_data(self, data: List[Tuple[RaiModel, List[TrafficHistoryModel]]]) -> bool:
        try:
            database = MongoRaiQuery()
            historyHandler = HistoryUpdaterHandler()
            for interface, traffic in track(data, description="Saving data in the database..."):
                try:
                    if not database.get_interface(interface.interface):
                        response = database.new_interface(interface)
                        if not response:
                            raise Exception(f"Failed to insert new interface of Rai layer: {interface.interface}")
                    for new_traffic in traffic:
                        new_traffic.idLayer = interface.interface
                        new_traffic.typeLayer = TableNameDatabase.RAI
                    response = historyHandler.load_data(data=traffic)
                    if not response:
                        raise Exception(f"Failed to insert histories traffic of an interface of Rai layer: {interface.interface}")
                except Exception as e:
                    LogHandler.log(f"Failed to insert new interface or histories traffic of Rai layer. {e}", err=True)
                    continue
        except Exception as e:
            LogHandler.log(f"Failed to load data of Rai layer. {e}", err=True)
            return False
        else:
            return True
