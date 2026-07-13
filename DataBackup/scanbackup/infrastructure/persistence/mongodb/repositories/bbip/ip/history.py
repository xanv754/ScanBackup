from datetime import date
from pymongo import ReplaceOne
from pymongo.errors import BulkWriteError

from scanbackup.domain import (
    IPActiveBBIPEntity,
    IPActiveBBIPField,
    IPHistoryBBIPRepository,
)
from scanbackup.shared import (
    Configuration,
    MongoInsertFailedError,
    MongoGetFailedError,
    MongoConnectionError,
)
from scanbackup.infrastructure.persistence.mongodb.connections.database import (
    MongoDatabase,
)
from scanbackup.infrastructure.persistence.mongodb.constants.collection import (
    MongoCollectionName,
    SuffixCollectionName,
)


class MongoIPHistoryBBIPRepository(IPHistoryBBIPRepository):
    name_collection: str

    def __init__(self, name_collection: str) -> None:
        self.name_collection = (
            name_collection.upper() + "_" + SuffixCollectionName.IP_HISTORIES.value
        )

    def _get_collection(self, client: MongoDatabase, name_collection: str):
        config = Configuration().get_cfg_database()
        client.set_uri(config)
        client.open_connection()
        database = client.get_connection()
        return database[name_collection]

    def insert(self, data: list[IPActiveBBIPEntity]) -> None:
        if not data:
            return

        client = MongoDatabase()
        try:
            sources_collection = self._get_collection(
                client, MongoCollectionName.IP_SOURCES.value
            )
            valid_devices = {
                doc["_id"]
                for doc in sources_collection.find(
                    {"_id": {"$in": list({e.device for e in data})}}, {"_id": 1}
                )
            }

            operations = [
                ReplaceOne(
                    filter={
                        IPActiveBBIPField.DEVICE.value: entity.device,
                        IPActiveBBIPField.DATE.value: entity.date.isoformat(),
                        IPActiveBBIPField.TIME.value: entity.time.isoformat(),
                    },
                    replacement={
                        IPActiveBBIPField.DATE.value: entity.date.isoformat(),
                        IPActiveBBIPField.TIME.value: entity.time.isoformat(),
                        IPActiveBBIPField.IN_PROM.value: entity.in_prom,
                        IPActiveBBIPField.IN_MAX.value: entity.in_max,
                        IPActiveBBIPField.DEVICE.value: entity.device,
                    },
                    upsert=True,
                )
                for entity in data
                if entity.device in valid_devices
            ]

            if not operations:
                return

            collection = self._get_collection(client, self.name_collection)
            collection.bulk_write(operations, ordered=False)
        except MongoConnectionError:
            raise
        except BulkWriteError as error:
            raise MongoInsertFailedError(
                error=error,
                extra_msg=f"Fallo en la inserción bulk en la colección {self.name_collection}",
            )
        except Exception as error:
            raise MongoInsertFailedError(
                error=error,
                extra_msg=f"Fallo al insertar nuevos valores históricos en la colección {self.name_collection}",
            )
        finally:
            client.close_connection()

    def get_by_date(self, target_date: date) -> list[IPActiveBBIPEntity]:
        client = MongoDatabase()
        try:
            collection = self._get_collection(client, self.name_collection)
            documents = collection.find(
                {IPActiveBBIPField.DATE.value: target_date.isoformat()}
            )
            return [
                IPActiveBBIPEntity(
                    date=doc[IPActiveBBIPField.DATE.value],
                    time=doc[IPActiveBBIPField.TIME.value],
                    in_prom=doc[IPActiveBBIPField.IN_PROM.value],
                    in_max=doc[IPActiveBBIPField.IN_MAX.value],
                    device=doc[IPActiveBBIPField.DEVICE.value],
                )
                for doc in documents
            ]
        except MongoConnectionError:
            raise
        except Exception as error:
            raise MongoGetFailedError(
                name_collection=self.name_collection, error=error
            )
        finally:
            client.close_connection()
