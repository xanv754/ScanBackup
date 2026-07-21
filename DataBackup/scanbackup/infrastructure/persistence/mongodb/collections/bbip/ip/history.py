from pathlib import Path
from pymongo import ASCENDING
from pymongo.database import Database
from scanbackup.domain import IPActiveBBIPField
from scanbackup.infrastructure.persistence.mongodb.schemas.bbip.ip.active import (
    IP_HISTORY_SCHEMA,
)
from scanbackup.infrastructure.persistence.mongodb.collections import mongo_io
from scanbackup.infrastructure.readers import IPHistoryBBIPImport
from scanbackup.infrastructure.writers import CSVWriter
from scanbackup.infrastructure.persistence.mongodb.dto.bbip.ip.history import (
    MongoIPHistoryBBIPDTO,
)


class IPHistoryBBIPCollection:
    """Mongo collection for a single BBIP layer's active-IP history (e.g. `DINT_IP_HISTORY_BBIP`)."""

    @staticmethod
    def _indexes(name_collection: str) -> tuple[mongo_io.IndexSpec, ...]:
        """Build the unique device/date/time index and the secondary date index."""
        return (
            (
                [
                    (IPActiveBBIPField.DEVICE.value, ASCENDING),
                    (IPActiveBBIPField.DATE.value, ASCENDING),
                    (IPActiveBBIPField.TIME.value, ASCENDING),
                ],
                True,
                f"unique_ip_{name_collection.lower()}",
            ),
            (
                [(IPActiveBBIPField.DATE.value, ASCENDING)],
                False,
                f"date_ip_{name_collection.lower()}",
            ),
        )

    @staticmethod
    def create(name_collection: str, database: Database) -> None:
        mongo_io.create_collection(
            name_collection,
            database,
            IP_HISTORY_SCHEMA,
            IPHistoryBBIPCollection._indexes(name_collection),
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
            MongoIPHistoryBBIPDTO,
            CSVWriter,
            dirpath,
            include_id,
        )

    @staticmethod
    def import_data(
        name_collection: str,
        database: Database,
        input_path: Path,
        delimiter: str,
    ) -> None:
        mongo_io.import_upsert_by_key(
            name_collection,
            database,
            IPHistoryBBIPImport,
            input_path,
            delimiter,
            (
                IPActiveBBIPField.DEVICE.value,
                IPActiveBBIPField.DATE.value,
                IPActiveBBIPField.TIME.value,
            ),
        )
