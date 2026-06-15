from pymongo import ReplaceOne
from pymongo.errors import BulkWriteError

from scanbackup.domain import (
    TrafficBBIPEntity,
    TrafficBBIPField,
    TrafficHistoryBBIPRepository,
)
from scanbackup.shared import (
    Configuration,
    MongoInsertFailedError,
    MongoConnectionError,
)
from scanbackup.infrastructure.persistence.mongodb.connections.database import (
    MongoDatabase,
)
from scanbackup.infrastructure.persistence.mongodb.constants.collection import (
    MongoCollectionName,
    SuffixCollectionName,
)


class MongoTrafficHistoryBBIPRepository(TrafficHistoryBBIPRepository):
    name_collection: str

    def __init__(self, name_collection: str) -> None:
        self.name_collection = (
            name_collection.upper() + "_" + SuffixCollectionName.TRAFFIC_HISTORIES.value
        )

    def _get_collection(self, client: MongoDatabase, name_collection: str):
        config = Configuration().get_cfg_database()
        client.set_uri(config)
        client.open_connection()
        database = client.get_connection()
        return database[name_collection]

    def insert(self, data: list[TrafficBBIPEntity]) -> None:
        if not data:
            return

        client = MongoDatabase()
        try:
            sources_collection = self._get_collection(
                client, MongoCollectionName.TRAFFIC_SOURCES.value
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
                        TrafficBBIPField.DEVICE.value: entity.device,
                        TrafficBBIPField.DATE.value: entity.date.isoformat(),
                        TrafficBBIPField.TIME.value: entity.time.isoformat(),
                    },
                    replacement={
                        TrafficBBIPField.DATE.value: entity.date.isoformat(),
                        TrafficBBIPField.TIME.value: entity.time.isoformat(),
                        TrafficBBIPField.IN_PROM.value: entity.in_prom,
                        TrafficBBIPField.IN_MAX.value: entity.in_max,
                        TrafficBBIPField.OUT_PROM.value: entity.out_prom,
                        TrafficBBIPField.OUT_MAX.value: entity.out_max,
                        TrafficBBIPField.DEVICE.value: entity.device,
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
