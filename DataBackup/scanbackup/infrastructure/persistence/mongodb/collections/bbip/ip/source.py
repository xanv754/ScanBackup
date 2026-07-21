from pathlib import Path
from pymongo import ASCENDING
from pymongo.database import Database
from scanbackup.domain import IPSourceBBIPField
from scanbackup.infrastructure.persistence.mongodb.constants.collection import (
    MongoCollectionName,
)
from scanbackup.infrastructure.persistence.mongodb.schemas.bbip.ip.source import (
    SOURCE_IP_BBIP_SCHEMA,
)
from scanbackup.infrastructure.persistence.mongodb.collections.operation import (
    CollectionOperation,
)
from scanbackup.infrastructure.persistence.mongodb.collections import mongo_io
from scanbackup.infrastructure.readers import IPSourceBBIPImport
from scanbackup.infrastructure.writers import CSVWriter
from scanbackup.infrastructure.persistence.mongodb.dto.bbip.ip.source import (
    MongoIPSourceBBIPDTO,
)


class IPSourceBBIPCollection(CollectionOperation):
    """Mongo collection for BBIP active-IP source interfaces (`IP_SOURCE_BBIP`)."""

    _NAME = MongoCollectionName.IP_SOURCES.value
    _INDEXES: tuple[mongo_io.IndexSpec, ...] = (
        (
            [
                (IPSourceBBIPField.LAYER.value, ASCENDING),
                (IPSourceBBIPField.INTERFACE.value, ASCENDING),
            ],
            True,
            f"unique_{_NAME.lower()}",
        ),
        (
            [(IPSourceBBIPField.LAYER.value, ASCENDING)],
            False,
            f"layer_{_NAME.lower()}",
        ),
    )

    @staticmethod
    def create(database: Database) -> None:
        mongo_io.create_collection(
            IPSourceBBIPCollection._NAME,
            database,
            SOURCE_IP_BBIP_SCHEMA,
            IPSourceBBIPCollection._INDEXES,
        )

    @staticmethod
    def delete(database: Database) -> None:
        mongo_io.delete_collection(IPSourceBBIPCollection._NAME, database)

    @staticmethod
    def export_data(
        database: Database,
        dirpath: Path | None = None,
        include_id: bool = False,
    ) -> str:
        return mongo_io.export_collection(
            IPSourceBBIPCollection._NAME,
            database,
            MongoIPSourceBBIPDTO,
            CSVWriter,
            dirpath,
            include_id,
        )

    @staticmethod
    def import_data(
        database: Database,
        input_path: Path,
        delimiter: str,
    ) -> None:
        mongo_io.import_insert_many(
            IPSourceBBIPCollection._NAME,
            database,
            IPSourceBBIPImport,
            input_path,
            delimiter,
        )
