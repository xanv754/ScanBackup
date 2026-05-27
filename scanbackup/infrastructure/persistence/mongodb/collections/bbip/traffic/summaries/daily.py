import csv
from pathlib import Path
from bson import ObjectId
from pymongo import ASCENDING
from pymongo.database import Database
from pymongo.errors import CollectionInvalid, BulkWriteError
from scanbackup.shared import (
    DataContentError,
    FileEmptyError,
    MongoCreateCollectionError,
    MongoExportCollectionError,
    MongoImportCollectionError,
    MongoDeleteCollectionError,
)
from scanbackup.infrastructure.persistence.mongodb.constants.collection import (
    MongoCollectionName,
)
from scanbackup.infrastructure.persistence.mongodb.schemas.bbip.traffic.summaries.daily import (
    TrafficDailySummaryBBIPField,
    DAILY_SUMMARY_SCHEMA,
)


class TrafficDailySummaryBBIPCollection:
    _NAME = MongoCollectionName.TRAFFIC_DAILY_SUMMARY.value

    @staticmethod
    def create(database: Database) -> None:
        try:
            database.create_collection(
                name=TrafficDailySummaryBBIPCollection._NAME,
                validator=DAILY_SUMMARY_SCHEMA,
            )
            collection = database[TrafficDailySummaryBBIPCollection._NAME]
            collection.create_index(
                [
                    (TrafficDailySummaryBBIPField.DEVICE.value, ASCENDING),
                    (TrafficDailySummaryBBIPField.DATE.value, ASCENDING),
                ],
                unique=True,
                name=f"unique_{TrafficDailySummaryBBIPCollection._NAME.lower()}",
            )
            collection.create_index(
                [(TrafficDailySummaryBBIPField.DATE.value, ASCENDING)],
                name=f"date_{TrafficDailySummaryBBIPCollection._NAME.lower()}",
            )
        except CollectionInvalid as error:
            raise MongoCreateCollectionError(
                TrafficDailySummaryBBIPCollection._NAME,
                error=f"La colección no es válida para creación\n{error}",
            )
        except Exception as error:
            raise MongoCreateCollectionError(
                TrafficDailySummaryBBIPCollection._NAME, error=error
            )

    @staticmethod
    def delete(database: Database) -> None:
        try:
            collection = database[TrafficDailySummaryBBIPCollection._NAME]
            collection.delete_many({})
            collection.drop()
        except Exception as error:
            raise MongoDeleteCollectionError(
                TrafficDailySummaryBBIPCollection._NAME, error=error
            )

    @staticmethod
    def export_data(
        database: Database,
        output_path: Path,
        delimiter: str,
        include_id: bool = False,
    ) -> None:
        try:
            collection = database[TrafficDailySummaryBBIPCollection._NAME]
            projection = {} if include_id else {"_id": 0}
            documents = collection.find({}, projection)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("w", newline="", encoding="utf-8") as f:
                fields = (["_id"] if include_id else []) + [
                    field.value for field in TrafficDailySummaryBBIPField
                ]
                writer = csv.DictWriter(f, fieldnames=fields, delimiter=delimiter)
                writer.writeheader()
                for doc in documents:
                    doc[TrafficDailySummaryBBIPField.DEVICE.value] = str(
                        doc[TrafficDailySummaryBBIPField.DEVICE.value]
                    )
                    if include_id:
                        doc["_id"] = str(doc["_id"])
                    writer.writerow(doc)
        except Exception as error:
            raise MongoExportCollectionError(
                TrafficDailySummaryBBIPCollection._NAME, error=error
            )

    @staticmethod
    def import_data(
        database: Database,
        input_path: Path,
        delimiter: str,
    ) -> None:
        try:
            collection = database[TrafficDailySummaryBBIPCollection._NAME]
            with input_path.open("r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                documents = []
                for i, row in enumerate(reader, start=1):
                    row.pop("_id", None)

                    try:
                        row[TrafficDailySummaryBBIPField.DEVICE.value] = ObjectId(
                            row[TrafficDailySummaryBBIPField.DEVICE.value]
                        )
                    except (ValueError, KeyError):
                        raise DataContentError(
                            extra_msg=f"Valor inválido de id, línea {i}"
                        )

                    float_fields = [
                        (TrafficDailySummaryBBIPField.IN_MAX, "in max"),
                        (TrafficDailySummaryBBIPField.IN_PROM, "in prom"),
                        (TrafficDailySummaryBBIPField.OUT_MAX, "out max"),
                        (TrafficDailySummaryBBIPField.OUT_PROM, "out prom"),
                        (TrafficDailySummaryBBIPField.USE, "uso"),
                    ]
                    for field, label in float_fields:
                        try:
                            row[field.value] = float(row[field.value])
                        except (ValueError, KeyError):
                            raise DataContentError(
                                extra_msg=f"Valor inválido de {label}, línea {i}"
                            )

                    documents.append(row)
            if not documents:
                raise FileEmptyError(filepath=input_path)
            try:
                collection.insert_many(documents, ordered=False)
            except BulkWriteError as bwe:
                non_duplicate_errors = [
                    err
                    for err in bwe.details.get("writeErrors", [])
                    if err.get("code") != 11000
                ]
                if non_duplicate_errors:
                    raise MongoImportCollectionError(
                        TrafficDailySummaryBBIPCollection._NAME, error=bwe
                    )
        except MongoImportCollectionError:
            raise
        except Exception as error:
            raise MongoImportCollectionError(
                TrafficDailySummaryBBIPCollection._NAME, error=error
            )
