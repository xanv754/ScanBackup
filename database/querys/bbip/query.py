from abc import ABC, abstractmethod
from pandas import DataFrame
from model import BBIPModel


class BBIPQuery(ABC):
    """Query class for BBIP data."""
    
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
    def new_interface(self, new: BBIPModel) -> bool:
        """Register new interface.

        Parameters
        ----------
        new : BBIPModel
            New interface of BBIP to register.

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
