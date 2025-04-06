import os
import pandas as pd
from typing import List, Tuple
from rich.progress import track
from constants.path import PathConstant
from model.boder import BorderModel
from model.trafficHistory import TrafficHistoryModel
from updater.update import UpdaterHandler
from storage.querys.borde.mongo import MongoBordeQuery
from utils.log import LogHandler


class BordeUpdaterHandler(UpdaterHandler):
    """Border data updater handler."""

    def get_data(self) -> List[Tuple[BorderModel, List[TrafficHistoryModel]]]:
        try:
            if not os.path.exists(PathConstant.DATA_BORDER) or not os.path.isdir(PathConstant.DATA_BORDER):
                raise FileNotFoundError("Border folder not found.")
            files = [filename for filename in os.listdir(PathConstant.DATA_BORDER)]
            data: List[Tuple[BorderModel, List[TrafficHistoryModel]]] = []
            for filename in track(files, description="Reading data border..."):
                try:
                    model = filename.split("%")[0]
                    interface = filename.split("%")[1]
                    capacity = int(filename.split("%")[2])
                    interface_border = BorderModel(
                        interface=interface,
                        model=model,
                        capacity=capacity
                    )
                    traffic_border: List[TrafficHistoryModel] = []
                    with open(f"{PathConstant.DATA_BORDER}/{filename}", "r") as file:
                        lines = file.readlines()
                        for line in lines[1:]:
                            new_traffic = TrafficHistoryModel(
                                date=line.split(" ")[0],
                                time=line.split(" ")[1],
                                id_layer=interface,
                                type_layer="Borde",
                                in_prom=int(line.split(" ")[2]),
                                out_prom=int(line.split(" ")[3]),
                                in_max=int(line.split(" ")[4]),
                                out_max=int(line.split(" ")[5]),
                            )
                            traffic_border.append(new_traffic)
                except Exception as e:
                    LogHandler.log(f"Something went wrong to load data: {filename}. {e}", err=True)
                    continue
                else:
                    data.append((interface_border, traffic_border))
        except Exception as e:
            LogHandler.log(f"Failed to data load of Border layer. {e}", err=True)
            return []
        else:
            return data

    def load_data(self, data: List[Tuple[BorderModel, List[TrafficHistoryModel]]]) -> bool:
        try:
            database = MongoBordeQuery()
            for interface, traffic in track(data, description="Saving data in the database..."):
                if not database.get_interface(interface.interface):
                    database.new_interface(interface)
        except Exception as e:
            LogHandler.log(f"Failed to load data of Border layer. {e}", err=True)
            return False
        else:
            return True
