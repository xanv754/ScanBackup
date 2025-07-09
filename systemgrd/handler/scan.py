from abc import ABC, abstractmethod


class ScanHandler(ABC):
    """Class to get data of scan layer."""

    @abstractmethod
    def get_all_interfaces(self) -> None:
        """Get all data interfaces."""
        pass

    @abstractmethod
    def get_all_interfaces_by_date(self, date: str) -> None:
        """Get all data interfaces by date.
        
        Parameters
        ----------
        date: str
            Date of the data. Format: YYYY-MM-DD.
        """
        pass

    @abstractmethod
    def get_all_daily_report(self, date: str | None = None) -> None:
        """Get all daily report of a date.
        
        Parameters
        ----------
        date: str
            Date of the data. Format: YYYY-MM-DD. Default is yesterday.
        """
        pass