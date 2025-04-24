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
        """Get a traffic history.

        Parameters
        ----------
        date : str
            Date of traffic history.
        time : str
            Time of traffic history.
        id_layer : str
            ID of layer.

        Returns
        -------
            Traffic history model or None if not found.
        """
        pass

    @abstractmethod
    def get_traffic_layer_by_date(self, id_layer: str, date: str) -> List[TrafficHistoryModel]:
        """Get all traffic history of a layer by date.

        Parameters
        ----------
        id_layer : str
            ID of layer.
        date : str
            Date of traffic history.

        Returns
        -------
            List of traffic history model.
        """
        pass