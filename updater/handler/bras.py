import os
from typing import List, Tuple
from rich.progress import track
from constants.path import PathConstant
from model.bras import BrasModel
from model.trafficHistory import TrafficHistoryModel
from updater.update import UpdaterHandler
from updater.handler.history import HistoryUpdaterHandler
from storage.constant.tables import TableNameDatabase
from storage.querys.bras.mongo import MongoBrasQuery
from utils.log import LogHandler


class BrasUpdaterHandler(UpdaterHandler):
    """Bras data updater handler."""

    def get_data(self, filepath: str | None = None, date: str | None = None) -> List[Tuple[BrasModel, List[TrafficHistoryModel]]]:
        try:
            if not os.path.exists(PathConstant.SCAN_DATA_BRAS) or not os.path.isdir(PathConstant.SCAN_DATA_BRAS):
                raise FileNotFoundError("Bras folder not found.")
            files = [filename for filename in os.listdir(PathConstant.SCAN_DATA_BRAS)]
            data: List[Tuple[BrasModel, List[TrafficHistoryModel]]] = []
            for filename in track(files, description="Reading data bras..."):
                try:
                    type_interface = filename.split("%")[0]
                    brasname = filename.split("%")[1]
                    capacity = int(filename.split("%")[2])
                    bras = BrasModel(
                        name=brasname,
                        type=type_interface,
                        capacity=capacity
                    )
                    historyHandler = HistoryUpdaterHandler()
                    if date:
                        traffic_bras = historyHandler.get_data(filepath=f"{PathConstant.SCAN_DATA_BRAS}/{filename}", date=date)
                    else:
                        traffic_bras = historyHandler.get_data(filepath=f"{PathConstant.SCAN_DATA_BRAS}/{filename}")
                except Exception as e:
                    LogHandler.log(f"Something went wrong to load data: {filename}. {e}", err=True)
                    continue
                else:
                    data.append((bras, traffic_bras))
        except Exception as e:
            LogHandler.log(f"Failed to data load of Bras layer. {e}", err=True)
            return []
        else:
            return data

    def load_data(self, data: List[Tuple[BrasModel, List[TrafficHistoryModel]]]) -> bool:
        try:
            database = MongoBrasQuery()
            historyHandler = HistoryUpdaterHandler()
            for bras, traffic in track(data, description="Saving data in the database..."):
                try:
                    if not database.get_bras(brasname=bras.name, type=bras.type):
                        response = database.new_bras(bras)
                        if not response:
                            raise Exception(f"Failed to insert new bras: {bras.name} {bras.type}")
                    for new_traffic in traffic:
                        new_traffic.idLayer = bras.name
                        new_traffic.typeLayer = TableNameDatabase.BRAS
                    response = historyHandler.load_data(data=traffic)
                    if not response:
                        raise Exception(f"Failed to insert histories traffic of an bras: {bras.name} {bras.type}")
                except Exception as e:
                    LogHandler.log(f"Failed to insert new bras or histories traffic of Bras layer. {e}", err=True)
                    continue
        except Exception as e:
            LogHandler.log(f"Failed to load data of Bras layer. {e}", err=True)
            return False
        else:
            return True
