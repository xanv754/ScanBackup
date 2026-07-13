from abc import ABC, abstractmethod
from scanbackup.domain.entities.bbip.ip.source import IPSourceBBIPEntity


class IPSourceBBIPRepository(ABC):
    @abstractmethod
    def get_existing_keys(self) -> list[dict]:
        """Retrieve existing keys from the IP source collection.

        Queries all documents in the collection and returns only the fields
        corresponding to interface and layer, excluding the '_id'.

        Returns:
            list[dict]: A list of dictionaries, where each dictionary contains
                the projected fields from the collection.
        """
        pass

    @abstractmethod
    def upsert_sources(self, data: list[IPSourceBBIPEntity]) -> None:
        """Perform a bulk upsert (update or insert) operation on IP sources.

        Processes a list of entities and executes an unordered 'bulk_write'. For
        each entity, if a document matches the combination of interface and
        layer, it is updated; otherwise, a new document is inserted.

        Args:
            data (list[IPSourceBBIPEntity]): A list of entities to be inserted
                or updated in the database.
        """
        pass

    @abstractmethod
    def discontinue_missing(self, present_keys: list[dict]) -> None:
        """Mark IP sources as discontinued if they are missing from the provided list.

        Uses the '$nor' operator to identify all documents in the collection whose
        keys (interface and layer) do not match any of the items in
        'present_keys', updating their status to discontinued.

        Args:
            present_keys (list[dict]): List of dictionaries containing the
                interface and layer combinations that should remain active.
        """
        pass

    @abstractmethod
    def get_sources_by_layer(self, layer: str) -> list[IPSourceBBIPEntity]:
        """Retrieve active IP sources filtered by a specific layer.

        Queries the collection for all documents belonging to the given layer
        with an active status, excluding the MongoDB '_id' and mapping the
        results into domain entity instances.

        Args:
            layer (str): The name or identifier of the layer to filter by.
        """
        pass

    @abstractmethod
    def get_sources_by_layer_id(self, layer: str) -> list[IPSourceBBIPEntity]:
        """Retrieve active IP sources filtered by a specific layer.

        Queries the collection for all documents belonging to the given layer
        with an active status, mapping the MongoDB '_id' into the entity's
        'id' field.

        Args:
            layer (str): The name or identifier of the layer to filter by.
        """
        pass

    @abstractmethod
    def get_all_active_sources(self) -> list[IPSourceBBIPEntity]:
        """Retrieve every active IP source, regardless of its layer.

        Queries the collection for all documents with an active status across
        every layer, including the MongoDB '_id' and mapping the results into
        domain entity instances.

        Returns:
            list[IPSourceBBIPEntity]: Every active IP source in the collection.
        """
        pass

    @abstractmethod
    def get_all_sources(self) -> list[IPSourceBBIPEntity]:
        """Retrieve every IP source regardless of its layer or status.

        Queries every document in the collection, including discontinued
        sources, so historical data can still resolve a device.

        Returns:
            list[IPSourceBBIPEntity]: Every IP source in the collection.
        """
        pass
