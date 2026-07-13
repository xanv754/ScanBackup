from pymongo import ReplaceOne
from pymongo.errors import BulkWriteError

from scanbackup.domain import (
    TrafficHourSummaryBBIPEntity,
    TrafficHourSummaryBBIPRepository,
    TrafficHourSummaryBBIPField,
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
)


class MongoTrafficHourSummaryBBIPRepository(TrafficHourSummaryBBIPRepository):
    def _get_collection(self, client: MongoDatabase):
        config = Configuration().get_cfg_database()
        client.set_uri(config)
        client.open_connection()
        database = client.get_connection()
        return database[MongoCollectionName.TRAFFIC_HOUR_SUMMARY.value]

    def insert(self, data: list[TrafficHourSummaryBBIPEntity]) -> None:
        if not data:
            return

        client = MongoDatabase()
        try:
            collection = self._get_collection(client)

            operations = [
                ReplaceOne(
                    filter={
                        TrafficHourSummaryBBIPField.DEVICE.value: entity.device,
                        TrafficHourSummaryBBIPField.DATE.value: entity.date.isoformat(),
                        TrafficHourSummaryBBIPField.TIME.value: entity.time.isoformat(),
                    },
                    replacement={
                        TrafficHourSummaryBBIPField.DEVICE.value: entity.device,
                        TrafficHourSummaryBBIPField.DATE.value: entity.date.isoformat(),
                        TrafficHourSummaryBBIPField.TIME.value: entity.time.isoformat(),
                        TrafficHourSummaryBBIPField.IN_PROM.value: entity.in_prom,
                        TrafficHourSummaryBBIPField.IN_MAX.value: entity.in_max,
                        TrafficHourSummaryBBIPField.OUT_PROM.value: entity.out_prom,
                        TrafficHourSummaryBBIPField.OUT_MAX.value: entity.out_max,
                        TrafficHourSummaryBBIPField.USE.value: entity.use,
                    },
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
                extra_msg=f"Fallo en la inserción bulk en la colección {MongoCollectionName.TRAFFIC_HOUR_SUMMARY.value}",
            )
        except Exception as error:
            raise MongoInsertFailedError(
                error=error,
                extra_msg=f"Fallo al insertar nuevos valores históricos en la colección {MongoCollectionName.TRAFFIC_HOUR_SUMMARY.value}",
            )
        finally:
            client.close_connection()
