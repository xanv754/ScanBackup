from pathlib import Path
from pymongo import ASCENDING
from pymongo.database import Database
from scanbackup.domain import TrafficSourceBBIPField
from scanbackup.infrastructure.persistence.mongodb.constants.collection import (
    MongoCollectionName,
)
from scanbackup.infrastructure.persistence.mongodb.schemas.bbip.traffic.source import (
    SOURCE_TRAFFIC_BBIP_SCHEMA,
)
from scanbackup.infrastructure.persistence.mongodb.collections.operation import (
    CollectionOperation,
)
from scanbackup.infrastructure.persistence.mongodb.collections import mongo_io
from scanbackup.infrastructure.persistence.mongodb.dto.bbip.traffic.source import (
    MongoTrafficSourceBBIPDTO,
)

from scanbackup.infrastructure.readers import (
    TrafficSourceBBIPImport,
)
from scanbackup.infrastructure.writers import CSVWriter


class TrafficSourceBBIPCollection(CollectionOperation):
    """Mongo collection for BBIP traffic source interfaces (`TRAFFIC_SOURCE_BBIP`)."""

    _NAME = MongoCollectionName.TRAFFIC_SOURCES.value
    _INDEXES: tuple[mongo_io.IndexSpec, ...] = (
        (
            [
                (TrafficSourceBBIPField.LAYER.value, ASCENDING),
                (TrafficSourceBBIPField.MODEL.value, ASCENDING),
                (TrafficSourceBBIPField.INTERFACE.value, ASCENDING),
            ],
            True,
            f"unique_{_NAME.lower()}",
        ),
        (
            [(TrafficSourceBBIPField.LAYER.value, ASCENDING)],
            False,
            f"layer_{_NAME.lower()}",
        ),
    )

    @staticmethod
    def create(database: Database) -> None:
        mongo_io.create_collection(
            TrafficSourceBBIPCollection._NAME,
            database,
            SOURCE_TRAFFIC_BBIP_SCHEMA,
            TrafficSourceBBIPCollection._INDEXES,
        )

    @staticmethod
    def delete(database: Database) -> None:
        mongo_io.delete_collection(TrafficSourceBBIPCollection._NAME, database)

    @staticmethod
    def export_data(
        database: Database,
        dirpath: Path | None = None,
        include_id: bool = False,
    ) -> str:
        return mongo_io.export_collection(
            TrafficSourceBBIPCollection._NAME,
            database,
            MongoTrafficSourceBBIPDTO,
            CSVWriter,
            dirpath,
            include_id,
        )

    @staticmethod
    def import_data(
        database: Database, input_path: Path, delimiter: str | None = None
    ) -> None:
        mongo_io.import_insert_many(
            TrafficSourceBBIPCollection._NAME,
            database,
            TrafficSourceBBIPImport,
            input_path,
            delimiter,
        )
