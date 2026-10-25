import uuid
from collections.abc import Callable, Iterator
from datetime import UTC, datetime, timedelta

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from interface_sync.constants.enums import InterfaceStatus
from interface_sync.exceptions import (
    DatabaseError,
    DatabaseUnavailableError,
    MissingDatabaseSettingsError,
)
from interface_sync.persistence import (
    InterfaceChanges,
    InterfaceDocument,
    InterfaceModification,
    InterfaceRepository,
    MongoConnection,
    MongoSettings,
)

Document = Callable[..., InterfaceDocument]

pytestmark = pytest.mark.integration


@pytest.fixture
def connection() -> Iterator[MongoConnection]:
    """A connection to a throwaway database of the development MongoDB, dropped afterwards."""
    try:
        settings = MongoSettings.from_environment()
    except MissingDatabaseSettingsError:
        pytest.skip("MongoDB settings are not available in the environment")
    test_settings = settings.model_copy(
        update={"database": f"test_interface_sync_{uuid.uuid4().hex}"}
    )
    mongo_connection = MongoConnection(test_settings)
    try:
        mongo_connection.database.client.admin.command("ping")
    except PyMongoError:
        mongo_connection.close()
        pytest.skip("MongoDB is not reachable")
    yield mongo_connection
    mongo_connection.database.client.drop_database(test_settings.database)
    mongo_connection.close()


@pytest.fixture
def repository(connection: MongoConnection) -> InterfaceRepository:
    repository = InterfaceRepository(connection.database)
    repository.prepare()
    return repository


@pytest.fixture
def unreachable_repository() -> Iterator[InterfaceRepository]:
    client: MongoClient = MongoClient("127.0.0.1", 1, serverSelectionTimeoutMS=200)
    yield InterfaceRepository(client["unreachable"])
    client.close()


def register(repository: InterfaceRepository, *documents: InterfaceDocument) -> None:
    repository.apply(InterfaceChanges(registrations=list(documents)))


def test_prepare_creates_the_three_named_indexes(repository: InterfaceRepository):
    """The schema indexes exist with the names of database.md."""
    indexes = repository.get_collection().index_information()

    assert indexes["uq_scan_url"]["unique"] is True
    assert indexes["uq_scan_url"]["key"] == [("scan_url", 1)]
    assert indexes["idx_status"]["key"] == [("status", 1)]
    assert indexes["idx_layer_name"]["key"] == [("layer", 1), ("name", 1)]


def test_prepare_is_idempotent(repository: InterfaceRepository):
    """Running prepare again neither fails nor duplicates indexes."""
    repository.prepare()
    repository.prepare()

    assert len(repository.get_collection().index_information()) == 4


def test_registered_documents_are_read_back_as_models(
    repository: InterfaceRepository, make_document: Document, now: datetime
):
    """RF-007: stored interfaces come back with id, Enum status, float capacity and UTC dates."""
    register(
        repository,
        make_document(capacity_gbps=40, created_at=now, updated_at=now),
    )

    [stored] = repository.find_by_scan_urls(["http://scan/1.log"])

    assert stored.id is not None
    assert stored.status is InterfaceStatus.ACTIVE
    assert isinstance(stored.capacity_gbps, float)
    assert stored.created_at == now
    assert stored.created_at.tzinfo is not None
    assert stored.created_at.utcoffset() == timedelta(0)


def test_capacity_is_stored_as_a_bson_double(
    repository: InterfaceRepository, make_document: Document
):
    """Database rule 3: traffic capacity is always a Double, never an int."""
    register(repository, make_document(capacity_gbps=0))

    raw = repository.get_collection().find_one({"scan_url": "http://scan/1.log"})

    assert isinstance(raw["capacity_gbps"], float)
    assert raw["status"] == "activa"


def test_duplicate_scan_url_is_rejected_by_the_unique_index(
    repository: InterfaceRepository, make_document: Document
):
    """RF-007: an interface is never duplicated; the database enforces it."""
    register(repository, make_document())

    with pytest.raises(DatabaseError):
        register(repository, make_document(name="OTHER NAME"))

    assert repository.get_collection().count_documents({}) == 1


def test_modification_sets_only_changed_fields_status_and_updated_at(
    repository: InterfaceRepository, make_document: Document, earlier: datetime, now: datetime
):
    """RF-008/RF-009: one $set with the changed fields; created_at and the rest are untouched."""
    register(repository, make_document(status=InterfaceStatus.DECOMMISSIONED))

    repository.apply(
        InterfaceChanges(
            modifications=[
                InterfaceModification(
                    scan_url="http://scan/1.log",
                    updated_at=now,
                    field_changes={"name": ("IF-1", "RENAMED"), "capacity_gbps": (10.0, 100.0)},
                    status_change=(InterfaceStatus.DECOMMISSIONED, InterfaceStatus.ACTIVE),
                )
            ]
        )
    )

    [stored] = repository.find_by_scan_urls(["http://scan/1.log"])
    assert stored.name == "RENAMED"
    assert stored.capacity_gbps == 100.0
    assert stored.status is InterfaceStatus.ACTIVE
    assert stored.updated_at == now
    assert stored.created_at == earlier
    assert (stored.layer, stored.vendor) == ("BORDE", "HUAWEI")


def test_modification_of_an_unknown_scan_url_creates_nothing(
    repository: InterfaceRepository, now: datetime
):
    """RF-007: updates never insert; only registrations create documents."""
    repository.apply(
        InterfaceChanges(
            modifications=[
                InterfaceModification(
                    scan_url="http://scan/ghost.log",
                    updated_at=now,
                    field_changes={"name": ("a", "b")},
                )
            ]
        )
    )

    assert repository.get_collection().count_documents({}) == 0


def test_applying_nothing_is_a_no_op(repository: InterfaceRepository):
    """An empty change set does not call bulk_write (which would raise) and writes nothing."""
    repository.apply(InterfaceChanges())

    assert repository.get_collection().count_documents({}) == 0


def test_ordered_write_stops_at_the_first_error_and_keeps_what_was_applied(
    repository: InterfaceRepository, make_document: Document
):
    """RF-010: the bulk stops on the duplicate; earlier writes stay, later ones are not applied."""
    first = make_document(scan_url="http://scan/a.log")
    duplicate = make_document(scan_url="http://scan/a.log", name="DUPLICATE")
    never_reached = make_document(scan_url="http://scan/c.log")

    with pytest.raises(DatabaseError):
        register(repository, first, duplicate, never_reached)

    stored_urls = {document["scan_url"] for document in repository.get_collection().find()}
    assert stored_urls == {"http://scan/a.log"}


def test_find_by_scan_urls_returns_only_the_requested_ones(
    repository: InterfaceRepository, make_document: Document
):
    """The page query brings exactly the interfaces of the listing."""
    register(
        repository,
        make_document(scan_url="http://scan/a.log"),
        make_document(scan_url="http://scan/b.log"),
        make_document(scan_url="http://scan/c.log"),
    )

    found = repository.find_by_scan_urls({"http://scan/a.log", "http://scan/c.log", "http://x"})

    assert {document.scan_url for document in found} == {"http://scan/a.log", "http://scan/c.log"}


def test_find_by_scan_urls_with_nothing_returns_nothing(
    repository: InterfaceRepository, make_document: Document
):
    """An empty set of scan_urls matches no document."""
    register(repository, make_document())

    assert repository.find_by_scan_urls([]) == []


def test_find_active_by_layer_filters_by_layer_and_status(
    repository: InterfaceRepository, make_document: Document
):
    """RF-009: the layer decommission only considers active interfaces of that layer."""
    register(
        repository,
        make_document(scan_url="http://scan/borde-active.log", layer="BORDE"),
        make_document(
            scan_url="http://scan/borde-off.log",
            layer="BORDE",
            status=InterfaceStatus.DECOMMISSIONED,
        ),
        make_document(scan_url="http://scan/dist-active.log", layer="DIST"),
    )

    found = repository.find_active_by_layer("BORDE")

    assert [document.scan_url for document in found] == ["http://scan/borde-active.log"]


def test_find_active_by_layer_of_an_unknown_layer_is_empty(repository: InterfaceRepository):
    """A layer without interfaces yields an empty list."""
    assert repository.find_active_by_layer("NOPE") == []


def test_prepare_fails_when_the_database_is_unreachable(
    unreachable_repository: InterfaceRepository,
):
    """RF-013: an unreachable database at startup is a startup error."""
    with pytest.raises(DatabaseUnavailableError):
        unreachable_repository.prepare()


def test_reads_and_writes_fail_with_database_error_when_unreachable(
    unreachable_repository: InterfaceRepository, make_document: Document
):
    """RF-010: every driver failure is translated into DatabaseError."""
    with pytest.raises(DatabaseError):
        unreachable_repository.find_by_scan_urls(["http://scan/1.log"])
    with pytest.raises(DatabaseError):
        unreachable_repository.find_active_by_layer("BORDE")
    with pytest.raises(DatabaseError):
        unreachable_repository.apply(InterfaceChanges(registrations=[make_document()]))


def test_database_error_does_not_leak_connection_details(
    unreachable_repository: InterfaceRepository,
):
    """Secrets and hosts never reach log or terminal through the error cause."""
    with pytest.raises(DatabaseError) as error:
        unreachable_repository.find_by_scan_urls(["u"])

    assert error.value.cause == "error de base de datos"
    assert "127.0.0.1" not in error.value.cause


def test_connection_returns_timezone_aware_dates(connection: MongoConnection):
    """The client is tz_aware so dates are always read back as UTC."""
    collection = connection.database["probe"]
    collection.insert_one({"moment": datetime(2026, 1, 1, tzinfo=UTC)})

    assert collection.find_one()["moment"].tzinfo is not None
