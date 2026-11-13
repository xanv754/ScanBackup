from collections.abc import Collection

from pydantic_mongo import AbstractRepository
from pymongo import ASCENDING, IndexModel, InsertOne, UpdateOne
from pymongo.errors import PyMongoError

from interface_sync.constants.constants import (
    FIELD_LAYER,
    FIELD_NAME,
    FIELD_SCAN_URL,
    FIELD_STATUS,
    FIELD_UPDATED_AT,
    INTERFACES_COLLECTION,
    LAYER_NAME_INDEX,
    MONGO_IN_OPERATOR,
    MONGO_SET_OPERATOR,
    STATUS_INDEX,
    UNIQUE_SCAN_URL_INDEX,
)
from interface_sync.constants.enums import InterfaceStatus
from interface_sync.exceptions import DatabaseError, DatabaseUnavailableError
from interface_sync.persistence.interface_document import InterfaceDocument
from interface_sync.persistence.interface_modification import (
    InterfaceChanges,
    InterfaceModification,
)


class InterfaceRepository(AbstractRepository[InterfaceDocument]):
    """The only gateway to the `interfaces` collection.

    Reads are mapped to `InterfaceDocument` by `pydantic-mongo`. Writes go through one ordered
    `bulk_write`, which `save_many` cannot do, so a failure stops at the first error and keeps
    what was already applied [RF-010]. Every `PyMongoError` becomes a `DatabaseError`.
    """

    class Meta:
        collection_name = INTERFACES_COLLECTION

    def prepare(self) -> None:
        """Check that the database answers and create the indexes; idempotent.

        The unique index on `scan_url` is what guarantees that an interface is never duplicated.
        Raise `DatabaseUnavailableError` when the database cannot be reached or prepared.
        """
        try:
            self.get_collection().database.client.admin.command("ping")
            self.get_collection().create_indexes(
                [
                    IndexModel(
                        [(FIELD_SCAN_URL, ASCENDING)], name=UNIQUE_SCAN_URL_INDEX, unique=True
                    ),
                    IndexModel([(FIELD_STATUS, ASCENDING)], name=STATUS_INDEX),
                    IndexModel(
                        [(FIELD_LAYER, ASCENDING), (FIELD_NAME, ASCENDING)], name=LAYER_NAME_INDEX
                    ),
                ]
            )
        except PyMongoError as error:
            raise DatabaseUnavailableError(
                f"Base de datos no disponible ({type(error).__name__})"
            ) from error

    def find_by_scan_urls(self, scan_urls: Collection[str]) -> list[InterfaceDocument]:
        """Return the stored interfaces whose `scan_url` is in the given set, in one query."""
        return self._find({FIELD_SCAN_URL: {MONGO_IN_OPERATOR: list(scan_urls)}})

    def find_active_by_layer(self, layer: str) -> list[InterfaceDocument]:
        """Return the stored interfaces of a layer whose status is `activa`, in one query."""
        return self._find({FIELD_LAYER: layer, FIELD_STATUS: InterfaceStatus.ACTIVE.value})

    def apply(self, changes: InterfaceChanges) -> None:
        """Write registrations and modifications in a single ordered bulk operation.

        Each modification is one `$set` with only the changed fields, the status if it changes
        and `updated_at`. Raise `DatabaseError` on any database failure.
        """
        operations = [
            InsertOne(self.to_document(document)) for document in changes.registrations
        ] + [
            UpdateOne(
                {FIELD_SCAN_URL: modification.scan_url},
                {MONGO_SET_OPERATOR: self._build_update(modification)},
            )
            for modification in changes.modifications
        ]
        if not operations:
            return
        try:
            self.get_collection().bulk_write(operations, ordered=True)
        except PyMongoError as error:
            raise DatabaseError() from error

    def _find(self, query: dict) -> list[InterfaceDocument]:
        """Run a query and map the result; raise `DatabaseError` on any database failure."""
        try:
            return list(self.find_by(query))
        except PyMongoError as error:
            raise DatabaseError() from error

    @staticmethod
    def _build_update(modification: InterfaceModification) -> dict:
        """Build the `$set` body of a modification."""
        update = {field: new for field, (_, new) in modification.field_changes.items()}
        if modification.status_change is not None:
            update[FIELD_STATUS] = modification.status_change[1].value
        update[FIELD_UPDATED_AT] = modification.updated_at
        return update
