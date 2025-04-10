from abc import ABC, abstractmethod
from typing import List
from model.trafficHistory import TrafficHistoryModel


class HistoryTrafficQuery(ABC):
    """Query class for history traffic table."""

    @abstractmethod
    def new_histories(self, new_histories: List[TrafficHistoryModel]) -> bool:
        """Register new histories.

        Parameters
        ----------
        new_histories : List[TrafficHistoryModel]
            All histories of traffic to register.

        Returns
        -------
            Insertion status. If True, the histories has been registered correctly. Otherwise returns False.
        """
        pass

    # @abstractmethod
    # def get_interface(self, interface: str) -> dict | None :
    #     """Get interface.

    #     Parameters
    #     ----------
    #     interface : str
    #         Name interface.

    #     Returns
    #     -------
    #         Interface information. If the interface does not exist, returns None.
    #     """
    #     pass
