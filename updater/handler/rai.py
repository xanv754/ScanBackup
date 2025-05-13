import os
from typing import List, Tuple
from datetime import datetime
from constants import LayerType, DataPath
from database import MongoRaiQuery, PostgresRaiQuery
from model import RaiModel, TrafficHistoryModel
from updater import UpdaterHandler, TrafficHistoryUpdaterHandler
from utils import log


class RaiUpdaterHandler(UpdaterHandler):
    """Rai data updater handler."""

    def get_data(self, filepath: str | None = None, date: str | None = None) -> List[Tuple[RaiModel, List[TrafficHistoryModel]]]:
        try:
            if not filepath: filepath = DataPath.SCAN_DATA_RAI
            if not os.path.exists(filepath) or not os.path.isdir(filepath):
                raise FileNotFoundError("Rai folder not found.")
            files = [filename for filename in os.listdir(filepath)]
            data: List[Tuple[RaiModel, List[TrafficHistoryModel]]] = []
            for filename in files:
                try:
                    interface = filename.split("%")[1]
                    capacity = float(filename.split("%")[2])
                    interface_border = RaiModel(
                        id=None,
                        name=interface,
                        capacity=capacity,
                        createAt=datetime.now().strftime("%Y-%m-%d")
                    )
                    historyHandler = TrafficHistoryUpdaterHandler()
                    if date:
                        traffic_border = historyHandler.get_data(filepath=f"{filepath}/{filename}", date=date)
                    else:
                        traffic_border = historyHandler.get_data(filepath=f"{filepath}/{filename}")
                except Exception as e:
                    log.error(f"Something went wrong to load data: {filename}. {e}")
                    continue
                else:
                    data.append((interface_border, traffic_border))
        except Exception as e:
            log.error(f"Failed to data load of Caching layer. {e}")
            return []
        else:
            return data

    def load_data(self, data: List[Tuple[RaiModel, List[TrafficHistoryModel]]]) -> bool:
        failed = False
        try:
            database = MongoRaiQuery()
            historyHandler = TrafficHistoryUpdaterHandler()
            for interface, traffic in data:
                try:
                    data_interface = database.get_interface(interface.name)
                    if not data_interface:
                        response = database.new_interface(interface)
                        if not response:
                            raise Exception(f"Failed to insert new interface of Rai layer: {interface.name}")
                        else:
                            data_interface = database.get_interface(interface.name)
                            if not data_interface:
                                raise Exception(f"Failed to get new interface of Rai layer: {interface.name}")
                    for new_traffic in traffic:
                        new_traffic.idLayer = str(data_interface.id)
                        new_traffic.typeLayer = LayerType.RAI
                    response = historyHandler.load_data(data=traffic, mongo=True)
                    if not response:
                        raise Exception(f"Failed to insert histories traffic of an interface of Rai layer: {interface.name}")
                except Exception as e:
                    log.error(f"Failed to insert new interface or histories traffic of Rai layer. {e}")
                    continue
        except Exception as e:
            log.error(f"Failed to load data of Rai layer. {e}")
            failed = True
        try:
            database = PostgresRaiQuery()
            historyHandler = TrafficHistoryUpdaterHandler()
            for interface, traffic in data:
                try:
                    data_interface = database.get_interface(interface.name)
                    if not data_interface:
                        response = database.new_interface(interface)
                        if not response:
                            raise Exception(f"Failed to insert new interface of Rai layer: {interface.name}")
                        else:
                            data_interface = database.get_interface(interface.name)
                            if not data_interface:
                                raise Exception(f"Failed to get new interface of Rai layer: {interface.name}")
                    for new_traffic in traffic:
                        new_traffic.idLayer = str(data_interface.id)
                        new_traffic.typeLayer = LayerType.RAI
                    response = historyHandler.load_data(data=traffic, postgres=True)
                    if not response:
                        raise Exception(f"Failed to insert histories traffic of an interface of Rai layer: {interface.name}")
                except Exception as e:
                    log.error(f"Failed to insert new interface or histories traffic of Rai layer. {e}")
                    continue
        except Exception as e:
            log.error(f"Failed to load data of Rai layer. {e}")
            failed = True
        return not failed
