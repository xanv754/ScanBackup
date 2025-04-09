import pandas as pd
from typing import List, Tuple
from model.boder import BorderModel
from model.trafficHistory import TrafficHistoryModel
from abc import ABC, abstractmethod


class UpdaterHandler:
    """System data updater handler"""

    @abstractmethod
    def get_data(self, filepath: str | None = None) -> List:
        """Get data from files."""
        pass

    @abstractmethod
    def load_data(self, data: List) -> bool:
        """Load data in the database."""
        pass
