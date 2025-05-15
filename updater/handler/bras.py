import os
from multiprocessing import Process
from typing import List, Tuple
from datetime import datetime
from constants.group import BrasType, LayerType
from constants.path import DataPath
from database import MongoBrasQuery, PostgresBrasQuery
from model import BrasModel, TrafficHistoryModel
from updater import UpdaterHandler, TrafficHistoryUpdaterHandler
from utils.log import log


class BrasUpdaterHandler(UpdaterHandler):
    """Bras data updater handler."""

    def __load_database(self, data: List[Tuple[BrasModel, List[TrafficHistoryModel]]]) -> bool:
        """Load the data obtained in the principal database."""
        failed = False
        try:
            database = MongoBrasQuery()
            historyHandler = TrafficHistoryUpdaterHandler()
            for bras, traffic in data:
                try:
                    data_bras = database.get_interface(brasname=bras.name, type=bras.type)
                    if not data_bras:
                        response = database.new_interface(bras)
                        if not response:
                            raise Exception(f"Failed to insert new bras: {bras.name} {bras.type}")
                        else:
                            data_bras = database.get_interface(brasname=bras.name, type=bras.type)
                            if not data_bras:
                                raise Exception(f"Failed to get new bras: {bras.name} {bras.type}")
                    for new_traffic in traffic:
                        new_traffic.idLayer = str(data_bras.id)
                        new_traffic.typeLayer = LayerType.BRAS
                    response = historyHandler.load_data(data=traffic, mongo=True)
                    if not response:
                        raise Exception(f"Failed to insert histories traffic of an bras: {bras.name} {bras.type}")
                except Exception as e:
                    log.error(f"Failed to insert new bras or histories traffic of Bras layer. {e}")
                    continue
        except Exception as e:
            log.error(f"Failed to load data of Bras layer. {e}")
            failed = True
        return not failed
    
    def __load_backup_database(self, data: List[Tuple[BrasModel, List[TrafficHistoryModel]]]) -> bool:
        """Load the data obtained in the secundary database."""
        failed = False
        try:
            database = PostgresBrasQuery()
            historyHandler = TrafficHistoryUpdaterHandler()
            for bras, traffic in data:
                try:
                    data_bras = database.get_interface(brasname=bras.name, type=bras.type)
                    if not data_bras:
                        response = database.new_interface(bras)
                        if not response:
                            raise Exception(f"Failed to insert new bras: {bras.name} {bras.type}")
                        else:
                            data_bras = database.get_interface(brasname=bras.name, type=bras.type)
                            if not data_bras:
                                raise Exception(f"Failed to get new bras: {bras.name} {bras.type}")
                    for new_traffic in traffic:
                        new_traffic.idLayer = str(data_bras.id)
                        new_traffic.typeLayer = LayerType.BRAS
                    response = historyHandler.load_data(data=traffic, postgres=True)
                    if not response:
                        raise Exception(f"Failed to insert histories traffic of an bras: {bras.name} {bras.type}")
                except Exception as e:
                    log.error(f"Failed to insert new bras or histories traffic of Bras layer. {e}")
                    continue
        except Exception as e:
            log.error(f"Failed to load data of Histories Traffic of Bras layer. {e}")
            failed = True
        return not failed
            
    def get_data(self, filepath: str | None = None, date: str | None = None) -> List[Tuple[BrasModel, List[TrafficHistoryModel]]]:
        try:
            if not filepath: filepath = DataPath.SCAN_DATA_BRAS
            if not os.path.exists(filepath) or not os.path.isdir(filepath):
                raise FileNotFoundError("Bras folder not found.")
            files = [filename for filename in os.listdir(filepath)]
            data: List[Tuple[BrasModel, List[TrafficHistoryModel]]] = []
            for filename in files:
                try:
                    type_interface = filename.split("%")[0]
                    if "UP" in type_interface: type_interface = BrasType.UPLINK
                    elif "DOWN" in type_interface: type_interface = BrasType.DOWNLINK
                    brasname = filename.split("%")[1]
                    current_capacity = int(filename.split("%")[2])
                    bras = BrasModel(
                        id=None,
                        name=brasname,
                        type=type_interface,
                        capacity=current_capacity,
                        createAt=datetime.now().strftime("%Y-%m-%d")
                    )
                    historyHandler = TrafficHistoryUpdaterHandler()
                    if date:
                        traffic_bras = historyHandler.get_data(filepath=f"{filepath}/{filename}", date=date)
                    else:
                        traffic_bras = historyHandler.get_data(filepath=f"{filepath}/{filename}")
                except Exception as e:
                    log.error(f"Something went wrong to load data: {filename}. {e}")
                    continue
                else:
                    data.append((bras, traffic_bras))
        except Exception as e:
            log.error(f"Failed to data load of Bras layer. {e}")
            return []
        else:
            return data

    def load_data(self, data: List[Tuple[BrasModel, List[TrafficHistoryModel]]]) -> bool:
        try:
            load_mongo = Process(target=self.__load_database, args=(data,))
            load_postgres = Process(target=self.__load_backup_database, args=(data,))
            load_mongo.start()
            load_postgres.start()
            load_mongo.join()
            load_postgres.join()
        except Exception as e:
            log.error(f"Failed to load data of Bras layer. {e}")
            return False
        else:
            return True