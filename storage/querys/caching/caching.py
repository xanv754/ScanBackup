from abc import ABC, abstractmethod
from model.caching import CachingModel


class CachingQuery(ABC):
    """Query class for caching table."""

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
    def get_interface(self, interface: str) -> dict | None :
        """Get interface.

        Parameters
        ----------
        interface : str
            Name interface.

        Returns
        -------
            Caching information. If the interface does not exist, returns None.
        """
        pass
