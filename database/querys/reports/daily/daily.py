from abc import ABC, abstractmethod
from pandas import DataFrame


class DailyReportQuery(ABC):
    """Abstract class to get data of daily reports."""

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
    def new_report(self, data: DataFrame) -> bool:
        """Register new daily report.

        Parameters
        ----------
        data : DataFrame
            Data of daily report.
        Returns
        -------
            Insertion status. If True, the daily report has been registered correctly. Otherwise returns False.
        """
        pass

    @abstractmethod
    def get_report(self, layer_type: str, date: str) -> DataFrame:
        """Get a daily report.

        Parameters
        ----------
        layer_type : str
            Type name of the layer to consult.
        date : str
            Date of daily report. Format YYYY-MM-DD.

        Returns
        -------
            Daily report information. If the daily report does not exist, returns a empty DataFrame.
        """
        pass