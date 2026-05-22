from abc import ABC, abstractmethod
from typing import List
from pandas import DataFrame
from scanbackup.model import BBIPModel


class BBIPQuery(ABC):
    """Query class for BBIP data."""

    @abstractmethod
    def new_interface(self, collection: str, data: List[BBIPModel]) -> bool:
        """Register new interface.

        :param collection: Name of the collection to execute the query
        :type collection: str
        :param data: List of new interfaces of BBIP to register.
        :type data: List[BBIPModel]
        :return bool: Insertion status. If True, the interface has been registered correctly. Otherwise returns False.
        """
        pass

    @abstractmethod
    def get_interface(self, collection: str, name: str) -> DataFrame:
        """Get interface.

        :param collection: Name of the collection to execute the query
        :type collection: str
        :param name: Name of the interface
        :type name: str
        :return DataFrame: Data obtained from the query
        """
        pass

    @abstractmethod
    def get_interfaces(self, collection: str) -> DataFrame:
        """Get all interfaces.

        :param collection: Name of the collection to execute the query
        :type collection: str
        :return DataFrame: Data obtained from the query
        """
        pass

    @abstractmethod
    def get_interfaces_by_date(self, collection: str, date: str) -> DataFrame:
        """Get all interfaces by date.

        :param collection: Name of the collection to execute the query
        :type collection: str
        :param date: Date of the data. Format: YYYY-MM-DD
        :type date: str
        :return DataFrame: Data obtained from the query
        """
        pass
