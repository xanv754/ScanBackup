from pymongo import UpdateOne
from pymongo.errors import BulkWriteError

from scanbackup.domain import TrafficSourceBBIPRepository, TrafficSourceBBIPEntity
from scanbackup.infrastructure.persistence.mongodb.connections.database import (
    MongoDatabase,
)
from scanbackup.infrastructure.persistence.mongodb.constants.collection import (
    MongoCollectionName,
)
from scanbackup.infrastructure.persistence.mongodb.schemas.bbip.traffic.source import (
    TrafficSourceBBIPField,
)
from scanbackup.shared import (
    Configuration,
    SourceStatus,
    MongoInsertFailedError,
    MongoConnectionError,
    MongoGetFailedError,
)


class MongoTrafficSourceBBIPRepository(TrafficSourceBBIPRepository):
    def _get_collection(self, client: MongoDatabase):
        config = Configuration().get_cfg_database()
        client.set_uri(config)
        client.open_connection()
        database = client.get_connection()
        return database[MongoCollectionName.TRAFFIC_SOURCES.value]

    def get_existing_keys(self) -> list[dict]:
        """Retrieve existing keys from the traffic source collection.

        Queries all documents in the collection and returns only the fields
        corresponding to interface, layer, and type, excluding the '_id'.

        Returns:
            list[dict]: A list of dictionaries, where each dictionary contains
                the projected fields from the collection.
        """
        client = MongoDatabase()
        try:
            collection = self._get_collection(client)
            return list(
                collection.find(
                    {},
                    {
                        "_id": 0,
                        TrafficSourceBBIPField.INTERFACE.value: 1,
                        TrafficSourceBBIPField.LAYER.value: 1,
                        TrafficSourceBBIPField.TYPE.value: 1,
                    },
                )
            )
        except MongoConnectionError:
            raise
        except Exception as error:
            raise MongoGetFailedError(
                error=error,
                extra_msg="Fallo al obtener claves existentes",
                name_collection=MongoCollectionName.TRAFFIC_SOURCES.value,
            )
        finally:
            client.close_connection()

    def upsert_sources(self, data: list[TrafficSourceBBIPEntity]) -> None:
        """Perform a bulk upsert (update or insert) operation on traffic sources.

        Processes a list of entities and executes an unordered 'bulk_write'. For
        each entity, if a document matches the combination of interface, layer,
        and type, it is updated; otherwise, a new document is inserted.

        Args:
            data (list[TrafficSourceBBIPEntity]): A list of entities to be
                inserted or updated in the database.
        """
        client = MongoDatabase()
        try:
            collection = self._get_collection(client)
            operations = [
                UpdateOne(
                    filter={
                        TrafficSourceBBIPField.INTERFACE.value: entity.interface,
                        TrafficSourceBBIPField.LAYER.value: entity.layer,
                        TrafficSourceBBIPField.TYPE.value: entity.type,
                    },
                    update={"$set": entity.model_dump(exclude_none=True)},
                    upsert=True,
                )
                for entity in data
            ]
            collection.bulk_write(operations, ordered=False)
        except MongoConnectionError:
            raise
        except BulkWriteError as error:
            raise MongoInsertFailedError(
                error=error,
                extra_msg=f"Upsert parcial fallido en {MongoCollectionName.TRAFFIC_SOURCES.value}",
            )
        except Exception as error:
            raise MongoInsertFailedError(
                error=error, extra_msg="Fallo en upsert de fuentes"
            )
        finally:
            client.close_connection()

    def discontinue_missing(self, present_keys: list[dict]) -> None:
        """Mark traffic sources as discontinued if they are missing from the provided list.

        Uses the '$nor' operator to identify all documents in the collection whose
        keys (interface, layer, and type) do not match any of the items in
        'present_keys', updating their status to discontinued.

        Args:
            present_keys (list[dict]): List of dictionaries containing the
                interface, layer, and type combinations that should remain active.
        """
        client = MongoDatabase()
        try:
            collection = self._get_collection(client)
            collection.update_many(
                filter={
                    "$nor": [
                        {
                            TrafficSourceBBIPField.INTERFACE.value: k[
                                TrafficSourceBBIPField.INTERFACE.value
                            ],
                            TrafficSourceBBIPField.LAYER.value: k[
                                TrafficSourceBBIPField.LAYER.value
                            ],
                            TrafficSourceBBIPField.TYPE.value: k[
                                TrafficSourceBBIPField.TYPE.value
                            ],
                        }
                        for k in present_keys
                    ]
                },
                update={"$set": {"status": SourceStatus.DISCONTINUED.value}},
            )
        except MongoConnectionError:
            raise
        except Exception as error:
            raise MongoInsertFailedError(
                error=error,
                extra_msg="Fallo al discontinuar fuentes",
                name_collection=MongoCollectionName.TRAFFIC_SOURCES.value,
            )
        finally:
            client.close_connection()

    def get_sources_by_layer(self, layer: str) -> list[TrafficSourceBBIPEntity]:
        """Retrieve active traffic sources filtered by a specific layer.

        Queries the collection for all documents belonging to the given layer
        with an active status, excluding the MongoDB '_id' and mapping the
        results into domain entity instances.

        Args:
            layer (str): The name or identifier of the layer to filter by.
        """
        client = MongoDatabase()
        try:
            collection = self._get_collection(client)
            documents = collection.find(
                {
                    TrafficSourceBBIPField.LAYER.value: layer,
                    TrafficSourceBBIPField.STATUS.value: SourceStatus.ACTIVE.value,
                },
                {"_id": 0},
            )
            return [TrafficSourceBBIPEntity(**doc) for doc in documents]
        except MongoConnectionError:
            raise
        except Exception as error:
            raise MongoGetFailedError(
                name_collection=MongoCollectionName.TRAFFIC_SOURCES.value, error=error
            )
        finally:
            client.close_connection()
