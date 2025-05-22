from abc import ABC, abstractmethod
from pandas import DataFrame
from model import BordeModel


class BordeQuery(ABC):
    """Query class for borde table."""
    
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
    def new_interface(self, new: BordeModel) -> bool:
        """Register new interface.

        Parameters
        ----------
        new : BordeModel
            New interface of borde to register.

        Returns
        -------
            Insertion status. If True, the interface has been registered correctly. Otherwise returns False.
        """
        pass

    @abstractmethod
    def get_interface(self, name: str) -> DataFrame:
        """Get interface.

        Parameters
        ----------
        name : str
            Name interface.
        """
        pass

    @abstractmethod
    def get_interfaces(self) -> DataFrame:
        """Get all interfaces."""
        pass
