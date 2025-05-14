from abc import ABC, abstractmethod
from database import Database


class DatabaseFactory(ABC):
    """Database factory class."""

    @abstractmethod 
    def get_database(self, uri: str) -> Database:
        """Get the object database.
        
        Parameters
        ----------
        uri : str
            URI database.
        """
        pass