import pandas as pd
from typing import List
from storage.querys.borde.mongo import MongoBordeQuery
from storage.querys.history.mongo import MongoHistoryTrafficQuery
from model.boder import BordeModel, BordeTrafficModel
from utils.log import LogHandler

class BordeController:
    @staticmethod
    def get_interfaces() -> List[BordeModel]:
        """Get a list of all interfaces of Borde in the database."""
        try:
            borderQuery = MongoBordeQuery()
            return borderQuery.get_interfaces()
        except Exception as e:
            LogHandler.log(f"Failed in the controller to make requests to the database. {e}", path=__file__, err=True)
            return []

    @staticmethod
    def get_interface(interface: str) -> BordeModel | None:
        """Get an interface of Borde in the database.
        
        Parameters
        ----------
        interface : str
            Name interface.
        """
        try:
            borderQuery = MongoBordeQuery()
            return borderQuery.get_interface(name=interface)
        except Exception as e:
            LogHandler.log(f"Failed in the controller to make requests to the database. {e}", path=__file__, err=True)
            return None
        
    @staticmethod
    def get_traffic_by_date(date: str) -> List[BordeTrafficModel]:
        """Get a list of all interfaces with the traffic of Borde in the database filtered by a date.
        
        Parameters
        ----------
        date : str
            Date to consult. Format YYYY-MM-DD.
        """
        try:
            data: List[BordeTrafficModel] = []
            borderQuery = MongoBordeQuery()
            trafficQuery = MongoHistoryTrafficQuery()
            interfaces = borderQuery.get_interfaces()
            if interfaces:
                for interface in interfaces:
                    traffic = trafficQuery.get_all_traffic_date_by_id(id=interface.name, date=date)
                    for data_traffic in traffic:
                        data.append(
                            BordeTrafficModel(
                                interface=interface.name,
                                model=interface.model,
                                capacity=interface.capacity,
                                date=data_traffic.date,
                                time=data_traffic.time,
                                inProm=data_traffic.inProm,
                                inMax=data_traffic.inMax,
                                outProm=data_traffic.outProm,
                                outMax=data_traffic.outMax
                            )
                        )
        except Exception as e:
            LogHandler.log(f"Failed in the controller to make requests to the database. {e}", path=__file__, err=True)
            return []
        else:
            return data
        
    @staticmethod
    def get_pd_traffic_by_date(date: str) -> pd.DataFrame | None:
        """Get a dataframe of all interfaces with the traffic of Borde in the database filtered by a date.
        
        Parameters
        ----------
        date : str
            Date to consult. Format YYYY-MM-DD.
        """
        try:
            borderQuery = MongoBordeQuery()
            trafficQuery = MongoHistoryTrafficQuery()
            interfaces = borderQuery.get_interfaces()
            if interfaces:
                data: List[BordeTrafficModel] = []
                for interface in interfaces:
                    traffic = trafficQuery.get_all_traffic_date_by_id(id=interface.name, date=date)
                    for data_traffic in traffic:
                        data.append(
                            BordeTrafficModel(
                                interface=interface.name,
                                model=interface.model,
                                capacity=interface.capacity,
                                date=data_traffic.date,
                                time=data_traffic.time,
                                inProm=data_traffic.inProm,
                                inMax=data_traffic.inMax,
                                outProm=data_traffic.outProm,
                                outMax=data_traffic.outMax
                            )
                        )
                data_json = [i.model_dump() for i in data]
                return pd.read_json(data_json, orient="records")
            else:
                return None
        except Exception as e:
            LogHandler.log(f"Failed in the controller to make requests to the database. {e}", path=__file__, err=True)
            return None