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

    # @abstractmethod
    # def get_all_traffic_by_layer(self, layer_name: str) -> List[TrafficHistoryModel]:
    #     """Get a list of all traffic history filtered by a layer.

    #     Parameters
    #     ----------
    #     layer_name : str
    #         Name of layer.
    #     """
    #     pass

    # @abstractmethod
    # def get_all_traffic_by_id(self, id: str) -> List[TrafficHistoryModel]:
    #     """Get a list of all traffic history filtered by a ID layer.

    #     Parameters
    #     ----------
    #     id : str
    #         ID of layer.
    #     """
    #     pass

    # @abstractmethod
    # def get_all_traffic_by_date(self, date: str) -> List[TrafficHistoryModel]:
    #     """Get a list of all traffic history filtered by a date.

    #     Parameters
    #     ----------
    #     date : str
    #         Date to consult.
    #     """
    #     pass

    # @abstractmethod
    # def get_all_traffic_date_by_layer(self, layer_name: str, date: str) -> List[TrafficHistoryModel]:
    #     """Get a list of all traffic history filtered by a layer and a date.

    #     Parameters
    #     ----------
    #     layer_name : str
    #         Name of layer.
    #     date : str
    #         Date to consult.
    #     """
    #     pass

    # @abstractmethod
    # def get_all_traffic_date_by_id(self, id: str, date: str) -> List[TrafficHistoryModel]:
    #     """Get a list of all traffic history filtered by a id layer and a date.

    #     Parameters
    #     ----------
    #     id : str
    #         ID of layer.
    #     date : str
    #         Date to consult.
    #     """
    #     pass
