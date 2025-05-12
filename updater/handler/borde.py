import os
from typing import List, Tuple
from datetime import datetime
from constants.path import DataPath
from constants.group import ModelBordeType, LayerType
from model.boder import BordeModel
from model.trafficHistory import TrafficHistoryModel
from updater.update import UpdaterHandler
from updater.handler.traffic import TrafficHistoryUpdaterHandler
from database.querys.borde.mongo import MongoBordeQuery
# from database.querys.borde.postgres import PostgresBordeQuery
from utils.log import log


class BordeUpdaterHandler(UpdaterHandler):
    """Border data updater handler."""

    def get_data(self, filepath: str | None = None, date: str | None = None) -> List[Tuple[BordeModel, List[TrafficHistoryModel]]]:
        try:
            if not filepath:
                filepath = DataPath.SCAN_DATA_BORDER
            if not os.path.exists(filepath) or not os.path.isdir(filepath):
                raise FileNotFoundError("Border folder not found.")
            files = [filename for filename in os.listdir(filepath)]
            data: List[Tuple[BordeModel, List[TrafficHistoryModel]]] = []
            for filename in files:
                try:
                    if filename.split("%")[0] == ModelBordeType.CISCO:
                        model = ModelBordeType.CISCO
                    else:
                        model = ModelBordeType.HUAWEI
                    interface = filename.split("%")[1]
                    capacity = int(filename.split("%")[2])
                    interface_border = BordeModel(
                        id=None,
                        name=interface,
                        model=model,
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
            log.error(f"Failed to data load of Border layer. {e}")
            return []
        else:
            return data

    def load_data(self, data: List[Tuple[BordeModel, List[TrafficHistoryModel]]]) -> bool:
        failed = False
        try:
            database = MongoBordeQuery()
            historyHandler = TrafficHistoryUpdaterHandler()
            for interface, traffic in data:
                try:
                    data_interface = database.get_interface(interface.name)
                    if not data_interface:
                        response = database.new_interface(interface)
                        if not response:
                            raise Exception(f"Failed to insert new interface of Border layer: {interface.name}")
                        else:
                            data_interface = database.get_interface(interface.name)
                            if not data_interface:
                                raise Exception(f"Failed to get new interface of Border layer: {interface.name}")
                    for new_traffic in traffic:
                        new_traffic.idLayer = str(data_interface.id)
                        new_traffic.typeLayer = LayerType.BORDE
                    response = historyHandler.load_data(data=traffic, mongo=True)
                    if not response:
                        raise Exception(f"Failed to insert histories traffic of an interface of Border layer: {interface.name}")
                except Exception as e:
                    log.error(f"Failed to insert new interface or histories traffic of Border layer. {e}")
                    continue
        except Exception as e:
            log.error(f"Failed to load data of Border layer. {e}")
            failed = True
        # try:
        #     database = PostgresBordeQuery()
        #     historyHandler = TrafficHistoryUpdaterHandler()
        #     for interface, traffic in data:
        #         try:
        #             data_interface = database.get_interface(interface.name)
        #             if not data_interface:
        #                 response = database.new_interface(interface)
        #                 if not response:
        #                     raise Exception(f"Failed to insert new interface of Border layer: {interface.name}")
        #                 else:
        #                     data_interface = database.get_interface(interface.name)
        #                     if not data_interface:
        #                         raise Exception(f"Failed to get new interface of Border layer: {interface.name}")
        #             for new_traffic in traffic:
        #                 new_traffic.idLayer = str(data_interface.id)
        #                 new_traffic.typeLayer = LayerType.BORDE
        #             response = historyHandler.load_data(data=traffic, postgres=True)
        #             if not response:
        #                 raise Exception(f"Failed to insert histories traffic of an interface of Border layer: {interface.name}")
        #         except Exception as e:
        #             log.error(f"Failed to insert new interface or histories traffic of Border layer. {e}")
        #             continue
        # except Exception as e:
        #     log.error(f"Failed to load data of Border layer. {e}")
        #     failed = True
        return not failed
