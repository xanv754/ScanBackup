import pandas as pd
from typing import List, Tuple
from model.boder import BorderModel
from model.trafficHistory import TrafficHistoryModel
from abc import ABC, abstractmethod


class UpdaterHandler:
    """System data updater handler"""

    @abstractmethod
    def get_data(self, filepath: str | None = None, date: str | None = None) -> List:
        """Get data from files.

        Parameters
        ----------
        filepath : str | None
            Path to the file to be read.
        date : str | None
            Date to be used for filtering.
        """
        pass

    @abstractmethod
    def load_data(self, data: List) -> bool:
        """Load data in the database."""
        pass
