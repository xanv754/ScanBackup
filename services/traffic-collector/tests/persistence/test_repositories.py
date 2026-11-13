from datetime import UTC, datetime, timedelta

import pytest
from bson import ObjectId
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from tests.conftest import CommandRecorder
from traffic_collector.constants.constants import (
    INTERFACES_COLLECTION,
    TRAFFIC_DAILY_COLLECTION,
    TRAFFIC_SUMMARY_DAILY_COLLECTION,
)
from traffic_collector.domain import DailySummary, DailyTraffic, Sample
from traffic_collector.persistence import (
    InterfaceRepository,
    SummaryRepository,
    TrafficRepository,
)

pytestmark = pytest.mark.integration

DATE = "2026-11-05"
START = datetime(2026, 11, 5, 4, 0, tzinfo=UTC)


def make_daily(
    interface_id: ObjectId, layer: str = "BORDE", count: int = 3
) -> DailyTraffic:
    samples = tuple(
        Sample(START + timedelta(minutes=5 * i), 1, 2, 3, 4) for i in range(count)
    )
    return DailyTraffic(
        interface_id=interface_id, layer=layer, date=DATE, samples=samples
    )


def insert_interface(database: Database, layer: str, status: str, url: str) -> ObjectId:
    return (
        database[INTERFACES_COLLECTION]
        .insert_one({"layer": layer, "status": status, "scan_url": url, "name": url})
        .inserted_id
    )


def test_layers_are_distinct_and_ascending(database: Database) -> None:
    """Layers come distinct and ordered, including layers without active ones (RF-018, RF-019)."""
    insert_interface(database, "DIST", "activa", "u1")
    insert_interface(database, "BORDE", "activa", "u2")
    insert_interface(database, "BORDE", "activa", "u3")
    insert_interface(database, "IXP", "desincorporada", "u4")

    assert InterfaceRepository(database).layers() == ["BORDE", "DIST", "IXP"]


def test_no_interfaces_means_no_layers(database: Database) -> None:
    """An empty collection has no layers (RF-018)."""
    assert InterfaceRepository(database).layers() == []


def test_active_by_layer_returns_only_active_of_that_layer(database: Database) -> None:
    """Only active interfaces of the requested layer, with id and scan_url (RF-019)."""
    active_id = insert_interface(database, "BORDE", "activa", "url-active")
    insert_interface(database, "BORDE", "desincorporada", "url-decommissioned")
    insert_interface(database, "DIST", "activa", "url-other-layer")

    interfaces = InterfaceRepository(database).active_by_layer("BORDE")

    assert [(i.interface_id, i.scan_url) for i in interfaces] == [
        (active_id, "url-active")
    ]


def test_active_by_layer_is_a_single_query(
    database: Database, command_recorder: CommandRecorder
) -> None:
    """Reading a layer sends one query, not one per interface (RF-019)."""
    for index in range(5):
        insert_interface(database, "BORDE", "activa", f"url-{index}")
    before = command_recorder.count("find", INTERFACES_COLLECTION)

    InterfaceRepository(database).active_by_layer("BORDE")

    assert command_recorder.count("find", INTERFACES_COLLECTION) - before == 1


def test_save_creates_one_document_with_float_values(database: Database) -> None:
    """Saving creates the document with layer, samples and both timestamps (RF-025)."""
    interface_id = ObjectId()
    repository = TrafficRepository(database)

    repository.save(make_daily(interface_id))

    document = database[TRAFFIC_DAILY_COLLECTION].find_one(
        {"interface_id": interface_id}
    )
    assert document["layer"] == "BORDE"
    assert document["date"] == DATE
    assert len(document["samples"]) == 3
    assert isinstance(document["samples"][0]["in_avg"], float)
    assert document["created_at"] == document["updated_at"]


def test_save_twice_does_not_duplicate(database: Database) -> None:
    """Saving the same (interface, date) again replaces samples, never duplicates (RF-025)."""
    interface_id = ObjectId()
    times = iter([START, START + timedelta(hours=1)])
    repository = TrafficRepository(database, clock=lambda: next(times))

    repository.save(make_daily(interface_id, count=3))
    repository.save(make_daily(interface_id, count=5))

    documents = list(
        database[TRAFFIC_DAILY_COLLECTION].find({"interface_id": interface_id})
    )
    assert len(documents) == 1
    assert len(documents[0]["samples"]) == 5
    assert documents[0]["created_at"] == START
    assert documents[0]["updated_at"] == START + timedelta(hours=1)


def test_save_completes_a_document_with_empty_samples(database: Database) -> None:
    """A document with empty samples is completed, not duplicated (RF-025)."""
    interface_id = ObjectId()
    database[TRAFFIC_DAILY_COLLECTION].insert_one(
        {"interface_id": interface_id, "date": DATE, "samples": []}
    )

    TrafficRepository(database).save(make_daily(interface_id))

    documents = list(
        database[TRAFFIC_DAILY_COLLECTION].find({"interface_id": interface_id})
    )
    assert len(documents) == 1
    assert len(documents[0]["samples"]) == 3


def test_unique_index_rejects_duplicates(database: Database) -> None:
    """uq_interface_date forbids two documents for the same (interface, date) (RF-025)."""
    TrafficRepository(database).ensure_indexes()
    interface_id = ObjectId()
    collection = database[TRAFFIC_DAILY_COLLECTION]
    collection.insert_one({"interface_id": interface_id, "date": DATE, "samples": []})

    with pytest.raises(DuplicateKeyError):
        collection.insert_one(
            {"interface_id": interface_id, "date": DATE, "samples": []}
        )


def test_ensure_indexes_is_idempotent(database: Database) -> None:
    """Creating the indexes twice is harmless (RF-025)."""
    repository = TrafficRepository(database)

    repository.ensure_indexes()
    repository.ensure_indexes()

    names = {
        index["name"] for index in database[TRAFFIC_DAILY_COLLECTION].list_indexes()
    }
    assert {"uq_interface_date", "idx_date"} <= names


def test_ids_with_samples_filters_by_layer_date_and_non_empty(
    database: Database,
) -> None:
    """Only non-empty documents of that layer and date count as already collected (RF-020)."""
    repository = TrafficRepository(database)
    collected, empty, other_layer, other_date = (ObjectId() for _ in range(4))
    repository.save(make_daily(collected))
    database[TRAFFIC_DAILY_COLLECTION].insert_one(
        {"interface_id": empty, "layer": "BORDE", "date": DATE, "samples": []}
    )
    repository.save(make_daily(other_layer, layer="DIST"))
    other_day = make_daily(other_date)
    repository.save(
        DailyTraffic(other_day.interface_id, "BORDE", "2026-11-04", other_day.samples)
    )

    assert repository.interface_ids_with_samples("BORDE", DATE) == {collected}


def test_ids_with_samples_is_a_single_query(
    database: Database, command_recorder: CommandRecorder
) -> None:
    """The skip check sends one query per layer (RF-020)."""
    repository = TrafficRepository(database)
    for _ in range(5):
        repository.save(make_daily(ObjectId()))
    before = command_recorder.count("find", TRAFFIC_DAILY_COLLECTION)

    repository.interface_ids_with_samples("BORDE", DATE)

    assert command_recorder.count("find", TRAFFIC_DAILY_COLLECTION) - before == 1


def test_delete_day_removes_only_that_interface_and_date(database: Database) -> None:
    """Forced deletion removes the raw document of one interface and date (RF-021)."""
    repository = TrafficRepository(database)
    target, untouched = ObjectId(), ObjectId()
    repository.save(make_daily(target))
    repository.save(make_daily(untouched))

    repository.delete_day(target, DATE)

    remaining = database[TRAFFIC_DAILY_COLLECTION].distinct("interface_id")
    assert remaining == [untouched]


def test_summary_delete_day_removes_only_that_interface_and_date(
    database: Database,
) -> None:
    """Forced deletion removes the summary of one interface and date (RF-021)."""
    collection = database[TRAFFIC_SUMMARY_DAILY_COLLECTION]
    target, untouched = ObjectId(), ObjectId()
    collection.insert_many(
        [
            {"interface_id": target, "date": DATE},
            {"interface_id": target, "date": "2026-11-04"},
            {"interface_id": untouched, "date": DATE},
        ]
    )

    SummaryRepository(database).delete_day(target, DATE)

    remaining = {(d["interface_id"], d["date"]) for d in collection.find()}
    assert remaining == {(target, "2026-11-04"), (untouched, DATE)}


def test_traffic_daily_by_date_streams_only_that_date(database: Database) -> None:
    """The stored days of one date are read back as `DailyTraffic` (RF-026)."""
    repository = TrafficRepository(database)
    first, second = ObjectId(), ObjectId()
    repository.save(make_daily(first))
    repository.save(make_daily(second, layer="BRAS", count=2))
    other_day = make_daily(ObjectId())
    repository.save(
        DailyTraffic(other_day.interface_id, "BORDE", "2026-11-04", other_day.samples)
    )

    days = {daily.interface_id: daily for daily in repository.daily_by_date(DATE)}

    assert set(days) == {first, second}
    assert len(days[second].samples) == 2
    assert days[second].layer == "BRAS"
    assert days[first].samples == make_daily(first).samples


def test_summary_save_is_an_idempotent_upsert(database: Database) -> None:
    """Saving twice keeps one summary document with the latest values (RF-026)."""
    repository = SummaryRepository(database)
    repository.ensure_indexes()
    interface_id = ObjectId()

    repository.save(DailySummary(interface_id, DATE, 1, 2, 3, 4))
    repository.save(DailySummary(interface_id, DATE, 5, 6, 7, 8))

    documents = list(database[TRAFFIC_SUMMARY_DAILY_COLLECTION].find({}, {"_id": 0}))
    assert documents == [
        {
            "interface_id": interface_id,
            "date": DATE,
            "in_avg": 5.0,
            "out_avg": 6.0,
            "in_max": 7.0,
            "out_max": 8.0,
        }
    ]
    assert repository.interface_ids_with_summary(DATE) == {interface_id}
    assert repository.interface_ids_with_summary("2026-11-04") == set()
