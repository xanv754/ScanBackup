import os
from multiprocessing import Process
from typing import List, Tuple
from datetime import datetime
from constants.group import LayerType
from constants.path import DataPath
from database import MongoCachingQuery, PostgresCachingQuery
from model import CachingModel, TrafficHistoryModel, CachingFieldModel
from updater import UpdaterHandler, TrafficHistoryUpdaterHandler
from utils.log import log


class CachingUpdaterHandler(UpdaterHandler):
    """Caching data updater handler."""

    def _load_database(self, data: List[Tuple[CachingModel, List[TrafficHistoryModel]]], db_backup: bool = False) -> bool:
        """Load the data obtained in the principal database."""
        failed = False
        try:
            if db_backup: database = PostgresCachingQuery()
            else: database = MongoCachingQuery()
            historyHandler = TrafficHistoryUpdaterHandler()
            for interface, traffic in data:
                try:
                    data_interface = database.get_interface(interface.name)
                    if data_interface.empty:
                        response = database.new_interface(interface)
                        if not response:
                            raise Exception(f"Failed to insert new interface of Caching layer: {interface.name}")
                        else:
                            data_interface = database.get_interface(interface.name)
                            if data_interface.empty:
                                raise Exception(f"Failed to get new interface of Caching layer: {interface.name}")
                    for new_traffic in traffic:
                        new_traffic.idLayer = str(data_interface[CachingFieldModel.id].iloc[0])
                        new_traffic.typeLayer = LayerType.CACHING
                    if db_backup: response = historyHandler.load_data(data=traffic, postgres=True)
                    else: response = historyHandler.load_data(data=traffic, mongo=True)
                    if not response:
                        raise Exception(f"Failed to insert histories traffic of an interface of Caching layer: {interface.name}")
                except Exception as e:
                    log.error(f"Failed to insert new interface or histories traffic of Caching layer. {e}")
                    continue
        except Exception as e:
            log.error(f"Failed to load data of Caching layer. {e}")
            failed = True
        return not failed

    def get_data(self, filepath: str | None = None, date: str | None = None) -> List[Tuple[CachingModel, List[TrafficHistoryModel]]]:
        try:
            if not filepath: filepath = DataPath.SCAN_DATA_CACHING
            if not os.path.exists(filepath) or not os.path.isdir(filepath):
                raise FileNotFoundError("Caching folder not found.")
            files = [filename for filename in os.listdir(filepath)]
            data: List[Tuple[CachingModel, List[TrafficHistoryModel]]] = []
            for filename in files:
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
                    log.error(f"Something went wrong to load data: {filename}. {e}")
                    continue
                else:
                    data.append((interface_border, traffic_border))
        except Exception as e:
            log.error(f"Failed to data load of Caching layer. {e}")
            return []
        else:
            return data

    def load_data(self, data: List[Tuple[CachingModel, List[TrafficHistoryModel]]]) -> bool:
        try:
            load_mongo = Process(target=self._load_database, args=(data,))
            # load_postgres = Process(target=self._load_database, args=(data, True))
            load_mongo.start()
            # load_postgres.start()
            load_mongo.join()
            # load_postgres.join()
        except Exception as e:
            log.error(f"Failed to load data of Caching layer. {e}")
            return False
        else:
            return True
