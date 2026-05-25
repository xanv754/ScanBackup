from pymongo import UpdateOne
from pymongo.errors import BulkWriteError

from scanbackup.domain import TrafficBBIPSourceRepository, BBIPTrafficSourceEntity
from scanbackup.infrastructure.persistence.mongodb.connections.database import (
    MongoDatabase,
)
from scanbackup.infrastructure.persistence.mongodb.constants.collection import (
    MongoCollectionName,
)
from scanbackup.infrastructure.persistence.mongodb.schemas.bbip.traffic.source import (
    BBIPSourceField,
)
from scanbackup.shared import (
    Configuration,
    SourceStatus,
    MongoInsertFailedError,
    MongoConnectionError,
)


class MongoTrafficBBIPRepository(TrafficBBIPSourceRepository):
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
                        BBIPSourceField.INTERFACE.value: 1,
                        BBIPSourceField.LAYER.value: 1,
                        BBIPSourceField.TYPE.value: 1,
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
                        BBIPSourceField.INTERFACE.value: entity.interface,
                        BBIPSourceField.LAYER.value: entity.layer,
                        BBIPSourceField.TYPE.value: entity.type,
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
                            BBIPSourceField.INTERFACE.value: k[
                                BBIPSourceField.INTERFACE.value
                            ],
                            BBIPSourceField.LAYER.value: k[BBIPSourceField.LAYER.value],
                            BBIPSourceField.TYPE.value: k[BBIPSourceField.TYPE.value],
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
