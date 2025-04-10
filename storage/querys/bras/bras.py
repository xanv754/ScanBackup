from abc import ABC, abstractmethod
from model.bras import BrasModel


class BrasQuery(ABC):
    """Query class for bras table."""

    @abstractmethod
    def new_bras(self, new: BrasModel) -> bool:
        """Register new bras.

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
    def get_bras(self, brasname: str, type: str) -> dict | None :
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
