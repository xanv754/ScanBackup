from abc import ABC, abstractmethod
from typing import List
from model.trafficHistory import TrafficHistoryModel


class TrafficHistoryQuery(ABC):
    """Query class for history traffic table."""

    @abstractmethod
    def new_traffic(self, traffic: List[TrafficHistoryModel]) -> bool:
        """Register new traffic histories.

        Parameters
        ----------
        traffic : List[TrafficHistoryModel]
            All histories of traffic to register.

        Returns
        -------
            Insertion status. If True, the histories has been registered correctly. Otherwise returns False.
        """
        pass

    @abstractmethod
    def get_traffic(self, date: str, time: str, id_layer: str) -> TrafficHistoryModel | None:
        """Get a traffic of a layer.

        Parameters
        ----------
        date : str
            Date of traffic history. Format YYYY-MM-DD.
        time : str
            Time of traffic history. Format HH:MM:SS.
        id_layer : str
            ID of the layer to consult.

        Returns
        -------
            Traffic information. If the traffic does not exist, returns None.
        """
        pass

    @abstractmethod
    def get_traffic_layer_by_date(self, layer_type: str, interface_name: str, date: str) -> List[TrafficHistoryModel]:
        """Get all traffic history of a layer by a date.

        Parameters
        ----------
        layer_type : str
            Type name of the layer to consult.
        date : str
            Date of traffic history. Format YYYY-MM-DD.

        Returns
        -------
            List of traffic history model.
        """
        pass
