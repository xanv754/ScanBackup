from datetime import date
from pymongo import ReplaceOne
from pymongo.errors import BulkWriteError

from scanbackup.domain import (
    TrafficDailySummaryBBIPEntity,
    TrafficDailySummaryBBIPRepository,
    TrafficDailySummaryBBIPField,
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
)


class MongoTrafficDailySummaryBBIPRepository(TrafficDailySummaryBBIPRepository):
    def _get_collection(self, client: MongoDatabase):
        config = Configuration().get_cfg_database()
        client.set_uri(config)
        client.open_connection()
        database = client.get_connection()
        return database[MongoCollectionName.TRAFFIC_DAILY_SUMMARY.value]

    def insert(self, data: list[TrafficDailySummaryBBIPEntity]) -> None:
        if not data:
            return

        client = MongoDatabase()
        try:
            collection = self._get_collection(client)

            operations = [
                ReplaceOne(
                    filter={
                        TrafficDailySummaryBBIPField.DEVICE.value: entity.device,
                        TrafficDailySummaryBBIPField.DATE.value: entity.date.isoformat(),
                    },
                    replacement={
                        TrafficDailySummaryBBIPField.DEVICE.value: entity.device,
                        TrafficDailySummaryBBIPField.DATE.value: entity.date.isoformat(),
                        TrafficDailySummaryBBIPField.IN_PROM.value: entity.in_prom,
                        TrafficDailySummaryBBIPField.IN_MAX.value: entity.in_max,
                        TrafficDailySummaryBBIPField.OUT_PROM.value: entity.out_prom,
                        TrafficDailySummaryBBIPField.OUT_MAX.value: entity.out_max,
                        TrafficDailySummaryBBIPField.USE.value: entity.use,
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
                extra_msg=f"Fallo en la inserción bulk en la colección {MongoCollectionName.TRAFFIC_DAILY_SUMMARY.value}",
            )
        except Exception as error:
            raise MongoInsertFailedError(
                error=error,
                extra_msg=f"Fallo al insertar nuevos valores históricos en la colección {MongoCollectionName.TRAFFIC_DAILY_SUMMARY.value}",
            )
        finally:
            client.close_connection()

    def get_by_date(self, target_date: date) -> list[TrafficDailySummaryBBIPEntity]:
        client = MongoDatabase()
        try:
            collection = self._get_collection(client)
            documents = collection.find(
                {TrafficDailySummaryBBIPField.DATE.value: target_date.isoformat()}
            )
            return [
                TrafficDailySummaryBBIPEntity(
                    date=doc[TrafficDailySummaryBBIPField.DATE.value],
                    in_prom=doc[TrafficDailySummaryBBIPField.IN_PROM.value],
                    in_max=doc[TrafficDailySummaryBBIPField.IN_MAX.value],
                    out_prom=doc[TrafficDailySummaryBBIPField.OUT_PROM.value],
                    out_max=doc[TrafficDailySummaryBBIPField.OUT_MAX.value],
                    use=doc[TrafficDailySummaryBBIPField.USE.value],
                    device=doc[TrafficDailySummaryBBIPField.DEVICE.value],
                )
                for doc in documents
            ]
        except MongoConnectionError:
            raise
        except Exception as error:
            raise MongoGetFailedError(
                name_collection=MongoCollectionName.TRAFFIC_DAILY_SUMMARY.value,
                error=error,
            )
        finally:
            client.close_connection()

    def get_by_date_range(
        self, start_date: date, end_date: date
    ) -> list[TrafficDailySummaryBBIPEntity]:
        client = MongoDatabase()
        try:
            collection = self._get_collection(client)
            documents = collection.find(
                {
                    TrafficDailySummaryBBIPField.DATE.value: {
                        "$gte": start_date.isoformat(),
                        "$lte": end_date.isoformat(),
                    }
                }
            )
            return [
                TrafficDailySummaryBBIPEntity(
                    date=doc[TrafficDailySummaryBBIPField.DATE.value],
                    in_prom=doc[TrafficDailySummaryBBIPField.IN_PROM.value],
                    in_max=doc[TrafficDailySummaryBBIPField.IN_MAX.value],
                    out_prom=doc[TrafficDailySummaryBBIPField.OUT_PROM.value],
                    out_max=doc[TrafficDailySummaryBBIPField.OUT_MAX.value],
                    use=doc[TrafficDailySummaryBBIPField.USE.value],
                    device=doc[TrafficDailySummaryBBIPField.DEVICE.value],
                )
                for doc in documents
            ]
        except MongoConnectionError:
            raise
        except Exception as error:
            raise MongoGetFailedError(
                name_collection=MongoCollectionName.TRAFFIC_DAILY_SUMMARY.value,
                error=error,
            )
        finally:
            client.close_connection()
