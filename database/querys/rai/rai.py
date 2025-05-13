from typing import List
from abc import ABC, abstractmethod
from model import RaiModel


class RaiQuery(ABC):
    """Query class for rai table."""

    @abstractmethod
    def set_database(self, uri: str) -> None:
        """Set the connection database.
        
        Parameters
        ----------
        uri : str
            New URI to connection database.
        """
        pass

    @abstractmethod
    def new_interface(self, new: RaiModel) -> bool:
        """Register new interface.

        Parameters
        ----------
        new : RaiModel
            New interface to register.

        Returns
        -------
            Insertion status. If True, the interface has been registered correctly. Otherwise returns False.
        """
        pass

    @abstractmethod
    def get_interface(self, name: str) -> RaiModel | None :
        """Get interface.

        Parameters
        ----------
        name : str
            Name interface.

        Returns
        -------
            Rai information. If the interface does not exist, returns None.
        """
        pass

    @abstractmethod
    def get_interfaces(self) -> List[RaiModel]:
        """Get all interfaces to rai layer.

        Returns
        -------
            List of rai interfaces.
        """
        pass