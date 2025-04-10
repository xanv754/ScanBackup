import os
from typing import List, Tuple
from rich.progress import track
from constants.path import PathConstant
from model.caching import CachingModel
from model.trafficHistory import TrafficHistoryModel
from updater.update import UpdaterHandler
from updater.handler.history import HistoryUpdaterHandler
from storage.constant.tables import TableNameDatabase
from storage.querys.caching.mongo import MongoCachingQuery
from utils.log import LogHandler


class CachingUpdaterHandler(UpdaterHandler):
    """Caching data updater handler."""

    def get_data(self, filepath: str | None = None) -> List[Tuple[CachingModel, List[TrafficHistoryModel]]]:
        try:
            if not os.path.exists(PathConstant.SCAN_DATA_CACHING) or not os.path.isdir(PathConstant.SCAN_DATA_CACHING):
                raise FileNotFoundError("Caching folder not found.")
            files = [filename for filename in os.listdir(PathConstant.SCAN_DATA_CACHING)]
            data: List[Tuple[CachingModel, List[TrafficHistoryModel]]] = []
            for filename in track(files, description="Reading data caching..."):
                try:
                    service = filename.split("%")[0]
                    interface = filename.split("%")[1]
                    capacity = int(filename.split("%")[2])
                    interface_border = CachingModel(
                        interface=interface,
                        service=service,
                        capacity=capacity
                    )
                    historyHandler = HistoryUpdaterHandler()
                    traffic_border = historyHandler.get_data(filepath=f"{PathConstant.SCAN_DATA_CACHING}/{filename}")
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

    def load_data(self, data: List[Tuple[CachingModel, List[TrafficHistoryModel]]]) -> bool:
        try:
            database = MongoCachingQuery()
            historyHandler = HistoryUpdaterHandler()
            for interface, traffic in track(data, description="Saving data in the database..."):
                try:
                    if not database.get_interface(interface.interface):
                        response = database.new_interface(interface)
                        if not response:
                            raise Exception(f"Failed to insert new interface of Caching layer: {interface.interface}")
                    for new_traffic in traffic:
                        new_traffic.idLayer = interface.interface
                        new_traffic.typeLayer = TableNameDatabase.CACHING
                    response = historyHandler.load_data(data=traffic)
                    if not response:
                        raise Exception(f"Failed to insert histories traffic of an interface of Caching layer: {interface.interface}")
                except Exception as e:
                    LogHandler.log(f"Failed to insert new interface or histories traffic of Caching layer. {e}", err=True)
                    continue
        except Exception as e:
            LogHandler.log(f"Failed to load data of Caching layer. {e}", err=True)
            return False
        else:
            return True
