from typing import List
from abc import ABC, abstractmethod
from pandas import DataFrame
from systemgrd.model import DailyReportModel


class DailyReportQuery(ABC):
    """Abstract class to get data of daily reports."""

    @abstractmethod
    def new_report(self, data: List[DailyReportModel]) -> bool:
        """Register new daily report.

        :param data: List of data daily report.
        :type data: List[DailyReportModel]
        :return bool: Insertion status. If True, the daily report has been registered correctly. Otherwise returns False.
        """
        pass

    @abstractmethod
    def get_report(self, layer_type: str, date: str) -> DataFrame:
        """Get a daily report.

        :param layer_type: Type name of the layer to consult.
        :type layer_type: str
        :param date: Date of daily report. Format YYYY-MM-DD.
        :type date: str
        :returns DataFrame: Daily report information. If the daily report does not exist, returns a empty DataFrame.
        """
        pass
