from abc import ABC, abstractmethod


class BordeQuery(ABC):
    """Query class for borde table."""

    @abstractmethod
    def new_interface(self, interface: str, model: str, capacity: int) -> bool:
        """Register new interface.

        Parameters
        ----------
        interface : str
            Name interface.
        model : str
            Model interface.
        capacity : int
            Capacity interface.

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