from pathlib import Path
from pymongo import ASCENDING
from pymongo.database import Database
from scanbackup.domain import TrafficBBIPField
from scanbackup.infrastructure.persistence.mongodb.schemas.bbip.traffic.data import (
    BBIP_TRAFFIC_SCHEMA,
)
from scanbackup.infrastructure.persistence.mongodb.collections import mongo_io
from scanbackup.infrastructure.readers import (
    TrafficHistoryBBIPImport,
)
from scanbackup.infrastructure.persistence.mongodb.dto.bbip.traffic.history import (
    MongoTrafficHistoryBBIPDTO,
)
from scanbackup.infrastructure.writers import CSVWriter


class TrafficHistoryBBIPCollection:
    """Mongo collection for a single BBIP layer's traffic history (e.g. `BORDE_TRAFFIC_HISTORY_BBIP`)."""

    @staticmethod
    def _indexes(name_collection: str) -> tuple[mongo_io.IndexSpec, ...]:
        """Build the unique device/date/time index and the secondary date index."""
        return (
            (
                [
                    (TrafficBBIPField.DEVICE.value, ASCENDING),
                    (TrafficBBIPField.DATE.value, ASCENDING),
                    (TrafficBBIPField.TIME.value, ASCENDING),
                ],
                True,
                f"unique_traffic_{name_collection.lower()}",
            ),
            (
                [(TrafficBBIPField.DATE.value, ASCENDING)],
                False,
                f"date_traffic_{name_collection.lower()}",
            ),
        )

    @staticmethod
    def create(name_collection: str, database: Database) -> None:
        mongo_io.create_collection(
            name_collection,
            database,
            BBIP_TRAFFIC_SCHEMA,
            TrafficHistoryBBIPCollection._indexes(name_collection),
        )

    @staticmethod
    def delete(name_collection: str, database: Database) -> None:
        mongo_io.delete_collection(name_collection, database)

    @staticmethod
    def export_data(
        name_collection: str,
        database: Database,
        dirpath: Path | None = None,
        include_id: bool = False,
    ) -> str:
        return mongo_io.export_collection(
            name_collection,
            database,
            MongoTrafficHistoryBBIPDTO,
            CSVWriter,
            dirpath,
            include_id,
        )

    @staticmethod
    def import_data(
        name_collection: str,
        database: Database,
        input_path: Path,
        delimiter: str | None = None,
    ) -> None:
        mongo_io.import_upsert_by_key(
            name_collection,
            database,
            TrafficHistoryBBIPImport,
            input_path,
            delimiter,
            (
                TrafficBBIPField.DEVICE.value,
                TrafficBBIPField.DATE.value,
                TrafficBBIPField.TIME.value,
            ),
        )
