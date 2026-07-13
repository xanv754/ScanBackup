from abc import ABC, abstractmethod
from scanbackup.domain.entities.bbip.traffic.source import TrafficSourceBBIPEntity


class TrafficSourceBBIPRepository(ABC):
    @abstractmethod
    def get_existing_keys(self) -> list[dict]:
        """Retrieve existing keys from the traffic source collection.

        Queries all documents in the collection and returns only the fields
        corresponding to interface, layer, and type, excluding the '_id'.

        Returns:
            list[dict]: A list of dictionaries, where each dictionary contains
                the projected fields from the collection.
        """
        pass

    @abstractmethod
    def upsert_sources(self, data: list[TrafficSourceBBIPEntity]) -> None:
        """Perform a bulk upsert (update or insert) operation on traffic sources.

        Processes a list of entities and executes an unordered 'bulk_write'. For
        each entity, if a document matches the combination of interface, layer,
        and type, it is updated; otherwise, a new document is inserted.

        Args:
            data (list[TrafficSourceBBIPEntity]): A list of entities to be
                inserted or updated in the database.
        """
        pass

    @abstractmethod
    def discontinue_missing(self, present_keys: list[dict]) -> None:
        """Mark traffic sources as discontinued if they are missing from the provided list.

        Uses the '$nor' operator to identify all documents in the collection whose
        keys (interface, layer, and type) do not match any of the items in
        'present_keys', updating their status to discontinued.

        Args:
            present_keys (list[dict]): List of dictionaries containing the
                interface, layer, and type combinations that should remain active.
        """
        pass

    @abstractmethod
    def get_sources_by_layer(self, layer: str) -> list[TrafficSourceBBIPEntity]:
        """Retrieve active traffic sources filtered by a specific layer.

        Queries the collection for all documents belonging to the given layer
        with an active status, excluding the MongoDB '_id' and mapping the
        results into domain entity instances.

        Args:
            layer (str): The name or identifier of the layer to filter by.
        """
        pass

    @abstractmethod
    def get_sources_by_layer_id(self, layer: str) -> list[TrafficSourceBBIPEntity]:
        """Retrieve active traffic sources filtered by a specific layer.

        Queries the collection for all documents belonging to the given layer
        with an active status, including the MongoDB '_id' and mapping the
        results into domain entity instances.

        Args:
            layer (str): The name or identifier of the layer to filter by.
        """
        pass

    @abstractmethod
    def get_all_active_sources(self) -> list[TrafficSourceBBIPEntity]:
        """Retrieve every active traffic source, regardless of its layer.

        Queries the collection for all documents with an active status across
        every layer, including the MongoDB '_id' and mapping the results into
        domain entity instances.

        Returns:
            list[TrafficSourceBBIPEntity]: Every active traffic source in the
                collection.
        """
        pass

    @abstractmethod
    def get_all_sources(self) -> list[TrafficSourceBBIPEntity]:
        """Retrieve every traffic source regardless of its layer or status.

        Queries every document in the collection, including discontinued
        sources, so historical data can still resolve a device's capacity.

        Returns:
            list[TrafficSourceBBIPEntity]: Every traffic source in the
                collection.
        """
        pass
