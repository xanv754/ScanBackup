import os
from typing import List, Tuple
from datetime import datetime
from rich.progress import track
from constants.path import PathConstant
from constants.group import LayerType
from model.caching import CachingModel
from model.trafficHistory import TrafficHistoryModel
from updater.update import UpdaterHandler
from updater.handler.traffic import TrafficHistoryUpdaterHandler
from database.querys.caching.mongo import MongoCachingQuery
from database.querys.caching.postgres import PostgresCachingQuery
from utils.log import LogHandler


class CachingUpdaterHandler(UpdaterHandler):
    """Caching data updater handler."""

    def get_data(self, filepath: str | None = None, date: str | None = None) -> List[Tuple[CachingModel, List[TrafficHistoryModel]]]:
        try:
            if not filepath:
                filepath = PathConstant.SCAN_DATA_CACHING
            if not os.path.exists(filepath) or not os.path.isdir(filepath):
                raise FileNotFoundError("Caching folder not found.")
            files = [filename for filename in os.listdir(filepath)]
            data: List[Tuple[CachingModel, List[TrafficHistoryModel]]] = []
            for filename in track(files, description="Reading data caching..."):
                try:
                    service = filename.split("%")[0]
                    interface = filename.split("%")[1]
                    capacity = float(filename.split("%")[2])
                    interface_border = CachingModel(
                        id=None,
                        name=interface,
                        service=service,
                        capacity=capacity,
                        createAt=datetime.now().strftime("%Y-%m-%d")
                    )
                    historyHandler = TrafficHistoryUpdaterHandler()
                    if date:
                        traffic_border = historyHandler.get_data(filepath=f"{filepath}/{filename}", date=date)
                    else:
                        traffic_border = historyHandler.get_data(filepath=f"{filepath}/{filename}")
                except Exception as e:
                    log = LogHandler()
                    log.export(f"Something went wrong to load data: {filename}. {e}", err=True)
                    continue
                else:
                    data.append((interface_border, traffic_border))
        except Exception as e:
            log = LogHandler()
            log.export(f"Failed to data load of Caching layer. {e}", err=True)
            return []
        else:
            return data

    def load_data(self, data: List[Tuple[CachingModel, List[TrafficHistoryModel]]]) -> bool:
        failed = False
        try:
            database = MongoCachingQuery()
            historyHandler = TrafficHistoryUpdaterHandler()
            for interface, traffic in track(data, description="Saving data in mongo database..."):
                try:
                    data_interface = database.get_interface(interface.name)
                    if not data_interface:
                        response = database.new_interface(interface)
                        if not response:
                            raise Exception(f"Failed to insert new interface of Caching layer: {interface.name}")
                        else:
                            data_interface = database.get_interface(interface.name)
                            if not data_interface:
                                raise Exception(f"Failed to get new interface of Caching layer: {interface.name}")
                    for new_traffic in traffic:
                        new_traffic.idLayer = str(data_interface.id)
                        new_traffic.typeLayer = LayerType.CACHING
                    response = historyHandler.load_data(data=traffic, mongo=True)
                    if not response:
                        raise Exception(f"Failed to insert histories traffic of an interface of Caching layer: {interface.name}")
                except Exception as e:
                    log = LogHandler()
                    log.export(f"Failed to insert new interface or histories traffic of Caching layer. {e}", err=True)
                    continue
        except Exception as e:
            log = LogHandler()
            log.export(f"Failed to load data of Caching layer. {e}", err=True)
            failed = True
        finally:
            database.close_connection()
        try:
            database = PostgresCachingQuery()
            historyHandler = TrafficHistoryUpdaterHandler()
            for interface, traffic in track(data, description="Saving data in postgres database..."):
                try:
                    data_interface = database.get_interface(interface.name)
                    if not data_interface:
                        response = database.new_interface(interface)
                        if not response:
                            raise Exception(f"Failed to insert new interface of Caching layer: {interface.name}")
                        else:
                            data_interface = database.get_interface(interface.name)
                            if not data_interface:
                                raise Exception(f"Failed to get new interface of Caching layer: {interface.name}")
                    for new_traffic in traffic:
                        new_traffic.idLayer = str(data_interface.id)
                        new_traffic.typeLayer = LayerType.CACHING
                    response = historyHandler.load_data(data=traffic, postgres=True)
                    if not response:
                        raise Exception(f"Failed to insert histories traffic of an interface of Caching layer: {interface.name}")
                except Exception as e:
                    log = LogHandler()
                    log.export(f"Failed to insert new interface or histories traffic of Caching layer. {e}", err=True)
                    continue
        except Exception as e:
            log = LogHandler()
            log.export(f"Failed to load data of Caching layer. {e}", err=True)
            failed = True
        finally:
            database.close_connection()
        return not failed
