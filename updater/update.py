from typing import List
from abc import ABC, abstractmethod


class UpdaterHandler(ABC):
    """System data updater handler"""

    @abstractmethod
    def get_data(self, filepath: str | None = None, date: str | None = None) -> List:
        """Get data to be loaded in the database.

        Parameters
        ----------
        filepath : str | None
            Path to the file to be read.
        date : str | None
            Date to be used for filtering.
        """
        pass

    @abstractmethod
    def load_data(self, data: List, mongo: bool = False, postgres: bool = False, uri: str | None = None) -> bool | None:
        """Load data in the database.
        
        Parameters
        ----------
        data : List
            Data to be loaded.
        mongo : bool
            Insert data in mongo database.
        postgres : bool
            Insert data in postgres database.
        uri : str | None
            URI to connect to the database.
        """
        pass
