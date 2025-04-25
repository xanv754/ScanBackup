from abc import ABC, abstractmethod
from model.caching import CachingModel


class CachingQuery(ABC):
    """Query class for caching table."""
    
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
    def close_connection(self) -> None:
        """Close the connection to the database."""
        pass

    @abstractmethod
    def new_interface(self, new: CachingModel) -> bool:
        """Register new interface.

        Parameters
        ----------
        new : CachingModel
            New interface to register.

        Returns
        -------
            Insertion status. If True, the interface has been registered correctly. Otherwise returns False.
        """
        pass

    @abstractmethod
    def get_interface(self, name: str) -> CachingModel | None :
        """Get interface.

        Parameters
        ----------
        name : str
            Name interface.

        Returns
        -------
            Caching information. If the interface does not exist, returns None.
        """
        pass
