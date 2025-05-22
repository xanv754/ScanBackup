import os
from multiprocessing import Process
from typing import List, Tuple
from datetime import datetime
from constants.group import ModelBordeType, LayerType
from constants.path import DataPath
from database import MongoBordeQuery, PostgresBordeQuery
from model import BordeModel, TrafficHistoryModel, BordeFieldModel
from updater import UpdaterHandler, TrafficHistoryUpdaterHandler
from utils.log import log


class BordeUpdaterHandler(UpdaterHandler):
    """Border data updater handler."""

    def __load_database(self, data: List[Tuple[BordeModel, List[TrafficHistoryModel]]], db_backup: bool = False) -> bool:
        """Load the data obtained in the database."""
        failed = False
        try:
            if db_backup: database = PostgresBordeQuery()
            else: database = MongoBordeQuery()
            historyHandler = TrafficHistoryUpdaterHandler()
            for interface, traffic in data:
                try:
                    data_interface = database.get_interface(interface.name)
                    if data_interface.empty:
                        response = database.new_interface(interface)
                        if not response:
                            raise Exception(f"Failed to insert new interface of Border layer: {interface.name}")
                        else:
                            data_interface = database.get_interface(interface.name)
                            if data_interface.empty:
                                raise Exception(f"Failed to get new interface of Border layer: {interface.name}")
                    for new_traffic in traffic:
                        new_traffic.idLayer = str(data_interface[BordeFieldModel.id].iloc[0])
                        new_traffic.typeLayer = LayerType.BORDE
                    if db_backup: response = historyHandler.load_data(data=traffic, postgres=True)
                    else: response = historyHandler.load_data(data=traffic, mongo=True)
                    if not response:
                        raise Exception(f"Failed to insert histories traffic of an interface of Border layer: {interface.name}")
                except Exception as e:
                    log.error(f"Failed to insert new interface or histories traffic of Border layer. {e}")
                    continue
        except Exception as e:
            log.error(f"Failed to load data of Border layer. {e}")
            failed = True
        return not failed

    def get_data(self, filepath: str | None = None, date: str | None = None) -> List[Tuple[BordeModel, List[TrafficHistoryModel]]]:
        try:
            if not filepath: filepath = DataPath.SCAN_DATA_BORDER
            if not os.path.exists(filepath) or not os.path.isdir(filepath):
                raise FileNotFoundError("Border folder not found.")
            files = [filename for filename in os.listdir(filepath)]
            data: List[Tuple[BordeModel, List[TrafficHistoryModel]]] = []
            for filename in files:
                try:
                    if filename.split("%")[0] == ModelBordeType.CISCO: current_model = ModelBordeType.CISCO
                    else: current_model = ModelBordeType.HUAWEI
                    interface = filename.split("%")[1]
                    current_capacity = int(filename.split("%")[2])
                    interface_border = BordeModel(
                        id=None,
                        name=interface,
                        model=current_model,
                        capacity=current_capacity,
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
            log.error(f"Failed to data load of Border layer. {e}")
            return []
        else:
            return data

    def load_data(self, data: List[Tuple[BordeModel, List[TrafficHistoryModel]]]) -> bool:
        try:
            load_mongo = Process(target=self.__load_database, args=(data,))
            load_postgres = Process(target=self.__load_database, args=(data, True))
            load_mongo.start()
            load_postgres.start()
            load_mongo.join()
            load_postgres.join()
        except Exception as e:
            log.error(f"Failed to load data of Border layer. {e}")
            return False
        else:
            return True
    