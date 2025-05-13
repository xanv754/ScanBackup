from typing import List
from abc import ABC, abstractmethod
from model.bras import BrasModel


class BrasQuery(ABC):
    """Query class for bras table."""

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
    def new_interface(self, new: BrasModel) -> bool:
        """Register new interface bras.

        Parameters
        ----------
        new : BrasModel
            New bras to register.

        Returns
        -------
            Insertion status. If True, the bras has been registered correctly. Otherwise returns False.
        """
        pass

    @abstractmethod
    def get_interface(self, brasname: str, type: str) -> BrasModel | None :
        """Get bras.

        Parameters
        ----------
        brasname : str
            Name brasname.
        type : str
            Type of bras.

        Returns
        -------
            Bras information. If the brasname does not exist, returns None.
        """
        pass

    @abstractmethod
    def get_interfaces(self) -> List[BrasModel]:
        """Get all bras.

        Returns
        -------
            List of bras.
        """
        pass
