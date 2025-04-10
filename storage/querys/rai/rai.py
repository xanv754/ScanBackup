from abc import ABC, abstractmethod
from model.rai import RaiModel


class RaiQuery(ABC):
    """Query class for rai table."""

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
    def get_interface(self, interface: str) -> dict | None :
        """Get interface.

        Parameters
        ----------
        interface : str
            Name interface.

        Returns
        -------
            Rai information. If the interface does not exist, returns None.
        """
        pass
