from pymongo import UpdateOne
from pymongo.errors import BulkWriteError

from scanbackup.domain import (
    TrafficSourceBBIPRepository,
    TrafficSourceBBIPEntity,
    TrafficSourceBBIPField,
)
from scanbackup.shared import (
    Configuration,
    SourceStatus,
    MongoInsertFailedError,
    MongoConnectionError,
    MongoGetFailedError,
)
from scanbackup.infrastructure.persistence.mongodb.connections.database import (
    MongoDatabase,
)
from scanbackup.infrastructure.persistence.mongodb.constants.collection import (
    MongoCollectionName,
)


class MongoTrafficSourceBBIPRepository(TrafficSourceBBIPRepository):
    def _get_collection(self, client: MongoDatabase):
        config = Configuration().get_cfg_database()
        client.set_uri(config)
        client.open_connection()
        database = client.get_connection()
        return database[MongoCollectionName.TRAFFIC_SOURCES.value]

    def get_existing_keys(self) -> list[dict]:
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
                extra_msg=f"Fallo al discontinuar fuentes en {MongoCollectionName.TRAFFIC_SOURCES.value}",
            )
        finally:
            client.close_connection()

    def get_sources_by_layer(self, layer: str) -> list[TrafficSourceBBIPEntity]:
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

    def get_sources_by_layer_id(self, layer: str) -> list[TrafficSourceBBIPEntity]:
        client = MongoDatabase()
        try:
            collection = self._get_collection(client)
            documents = collection.find(
                {
                    TrafficSourceBBIPField.LAYER.value: layer,
                    TrafficSourceBBIPField.STATUS.value: SourceStatus.ACTIVE.value,
                }
            )
            return [
                TrafficSourceBBIPEntity(**{**doc, "device": str(doc["_id"]), "_id": None})
                for doc in documents
            ]
        except MongoConnectionError:
            raise
        except Exception as error:
            raise MongoGetFailedError(
                name_collection=MongoCollectionName.TRAFFIC_SOURCES.value, error=error
            )
        finally:
            client.close_connection()