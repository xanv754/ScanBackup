from abc import ABC, abstractmethod
from model.boder import BorderModel


class BordeQuery(ABC):
    """Query class for borde table."""

    @abstractmethod
    def new_interface(self, new: BorderModel) -> bool:
        """Register new interface.

        Parameters
        ----------
        new : BorderModel
            New interface of border to register.

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
            Interface information. If the interface does not exist, returns None.
        """
        pass
