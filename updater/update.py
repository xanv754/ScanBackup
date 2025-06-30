from typing import List
from abc import ABC, abstractmethod
from pandas import DataFrame


class UpdaterHandler(ABC):
    """System data updater handler"""
    @abstractmethod
    def get_data(self, folderpath: str | None = None, date: str | None = None) -> List:
        """Get data to be loaded in the database.

        Parameters
        ----------
        folderpath : str | None
            Path to the file to be read.
        date : str | None
            Date to be used for filtering.
        """
        pass

    @abstractmethod
    def load_data(self, data: DataFrame, uri: str | None = None) -> bool | None:
        """Load data in the database.
        
        Parameters
        ----------
        data : DataFrame
            Data to be loaded.
        uri : str | None
            URI to connect to the database.
        """
        pass
