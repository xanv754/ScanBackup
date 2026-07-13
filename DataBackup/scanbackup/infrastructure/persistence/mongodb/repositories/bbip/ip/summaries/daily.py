from pymongo import ReplaceOne
from pymongo.errors import BulkWriteError

from scanbackup.domain import (
    IPDailySummaryBBIPEntity,
    IPDailySummaryBBIPRepository,
    IPDailySummaryBBIPField,
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


class MongoIPDailySummaryBBIPRepository(IPDailySummaryBBIPRepository):
    def _get_collection(self, client: MongoDatabase):
        config = Configuration().get_cfg_database()
        client.set_uri(config)
        client.open_connection()
        database = client.get_connection()
        return database[MongoCollectionName.IP_DAILY_SUMMARY.value]

    def insert(self, data: list[IPDailySummaryBBIPEntity]) -> None:
        if not data:
            return

        client = MongoDatabase()
        try:
            collection = self._get_collection(client)

            operations = [
                ReplaceOne(
                    filter={
                        IPDailySummaryBBIPField.DEVICE.value: entity.device,
                        IPDailySummaryBBIPField.DATE.value: entity.date.isoformat(),
                    },
                    replacement={
                        IPDailySummaryBBIPField.DEVICE.value: entity.device,
                        IPDailySummaryBBIPField.DATE.value: entity.date.isoformat(),
                        IPDailySummaryBBIPField.IN_PROM.value: entity.in_prom,
                        IPDailySummaryBBIPField.IN_MAX.value: entity.in_max,
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
                extra_msg=f"Fallo en la inserción bulk en la colección {MongoCollectionName.IP_DAILY_SUMMARY.value}",
            )
        except Exception as error:
            raise MongoInsertFailedError(
                error=error,
                extra_msg=f"Fallo al insertar nuevos valores históricos en la colección {MongoCollectionName.IP_DAILY_SUMMARY.value}",
            )
        finally:
            client.close_connection()
