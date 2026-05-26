from pymongo import UpdateOne
from pymongo.errors import BulkWriteError

from scanbackup.domain import BBIPTrafficSourceRepository, BBIPTrafficSourceEntity
from scanbackup.infrastructure.persistence.mongodb.connections.database import (
    MongoDatabase,
)
from scanbackup.infrastructure.persistence.mongodb.constants.collection import (
    MongoCollectionName,
)
from scanbackup.infrastructure.persistence.mongodb.schemas.bbip.traffic.source import (
    BBIPTrafficSourceField,
)
from scanbackup.shared import (
    Configuration,
    SourceStatus,
    MongoInsertFailedError,
    MongoConnectionError,
    MongoGetFailedError,
)


class MongoBBIPTrafficRepository(BBIPTrafficSourceRepository):
    def _get_collection(self, client: MongoDatabase):
        config = Configuration().get_cfg_database()
        client.set_uri(config)
        client.open_connection()
        database = client.get_connection()
        return database[MongoCollectionName.BBIP_SOURCES.value]

    def get_existing_keys(self) -> list[dict]:
        client = MongoDatabase()
        try:
            collection = self._get_collection(client)
            return list(
                collection.find(
                    {},
                    {
                        "_id": 0,
                        BBIPTrafficSourceField.INTERFACE.value: 1,
                        BBIPTrafficSourceField.LAYER.value: 1,
                        BBIPTrafficSourceField.TYPE.value: 1,
                    },
                )
            )
        except MongoConnectionError:
            raise
        except Exception as error:
            raise MongoInsertFailedError(
                error=error, extra_msg="Fallo al obtener claves existentes"
            )
        finally:
            client.close_connection()

    def upsert_sources(self, data: list[BBIPTrafficSourceEntity]) -> None:
        client = MongoDatabase()
        try:
            collection = self._get_collection(client)
            operations = [
                UpdateOne(
                    filter={
                        BBIPTrafficSourceField.INTERFACE.value: entity.interface,
                        BBIPTrafficSourceField.LAYER.value: entity.layer,
                        BBIPTrafficSourceField.TYPE.value: entity.type,
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
                extra_msg=f"Upsert parcial fallido en {MongoCollectionName.BBIP_SOURCES.value}",
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
                            BBIPTrafficSourceField.INTERFACE.value: k[
                                BBIPTrafficSourceField.INTERFACE.value
                            ],
                            BBIPTrafficSourceField.LAYER.value: k[
                                BBIPTrafficSourceField.LAYER.value
                            ],
                            BBIPTrafficSourceField.TYPE.value: k[
                                BBIPTrafficSourceField.TYPE.value
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
                error=error, extra_msg="Fallo al discontinuar fuentes"
            )
        finally:
            client.close_connection()

    def get_sources_by_layer(self, layer: str) -> list[BBIPTrafficSourceEntity]:
        name_collection = MongoCollectionName.BBIP_SOURCES.value
        client = MongoDatabase()
        try:
            collection = self._get_collection(client)
            documents = collection.find(
                {
                    BBIPTrafficSourceField.LAYER.value: layer,
                    BBIPTrafficSourceField.STATUS.value: SourceStatus.ACTIVE.value,
                },
                {"_id": 0},
            )
            return [BBIPTrafficSourceEntity(**doc) for doc in documents]
        except MongoConnectionError:
            raise
        except Exception as error:
            raise MongoGetFailedError(name_collection, error=error)
        finally:
            client.close_connection()
