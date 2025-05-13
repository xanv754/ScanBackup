from abc import ABC, abstractmethod


class Database(ABC):
    @abstractmethod
    def get_connection(self):
        """Get a connection to the database."""
        pass

    @abstractmethod
    def get_cursor(self, table: str | None = None):
        """Get a cursor to the database."""
        pass

    @abstractmethod
    def open_connection(self) -> None:
        """Open a connection to the database."""
        pass

    @abstractmethod
    def close_connection(self) -> None:
        """Close the connection to the database."""
        pass

    @abstractmethod
    def migration(self) -> bool:
        """Run migrations.

        Returns
        -------
        Operation status. If True, the migrations have been executed correctly. Otherwise returns False.
        """
        pass

    @abstractmethod
    def rollback(self) -> bool:
        """Run rollback migrations.

        Returns
        -------
        Operation status. If True, the rollback migrations have been executed correctly. Otherwise returns False.
        """
        pass
