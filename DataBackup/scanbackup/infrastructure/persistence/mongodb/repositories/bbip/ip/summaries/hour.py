from pymongo import ReplaceOne
from pymongo.errors import BulkWriteError

from scanbackup.domain import (
    IPHourSummaryBBIPEntity,
    IPHourSummaryBBIPRepository,
    IPHourSummaryBBIPField,
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


class MongoIPHourSummaryBBIPRepository(IPHourSummaryBBIPRepository):
    def _get_collection(self, client: MongoDatabase):
        config = Configuration().get_cfg_database()
        client.set_uri(config)
        client.open_connection()
        database = client.get_connection()
        return database[MongoCollectionName.IP_HOUR_SUMMARY.value]

    def insert(self, data: list[IPHourSummaryBBIPEntity]) -> None:
        if not data:
            return

        client = MongoDatabase()
        try:
            collection = self._get_collection(client)

            operations = [
                ReplaceOne(
                    filter={
                        IPHourSummaryBBIPField.DEVICE.value: entity.device,
                        IPHourSummaryBBIPField.DATE.value: entity.date.isoformat(),
                        IPHourSummaryBBIPField.TIME.value: entity.time.isoformat(),
                    },
                    replacement={
                        IPHourSummaryBBIPField.DEVICE.value: entity.device,
                        IPHourSummaryBBIPField.DATE.value: entity.date.isoformat(),
                        IPHourSummaryBBIPField.TIME.value: entity.time.isoformat(),
                        IPHourSummaryBBIPField.IN_PROM.value: entity.in_prom,
                        IPHourSummaryBBIPField.IN_MAX.value: entity.in_max,
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
                extra_msg=f"Fallo en la inserción bulk en la colección {MongoCollectionName.IP_HOUR_SUMMARY.value}",
            )
        except Exception as error:
            raise MongoInsertFailedError(
                error=error,
                extra_msg=f"Fallo al insertar nuevos valores históricos en la colección {MongoCollectionName.IP_HOUR_SUMMARY.value}",
            )
        finally:
            client.close_connection()
