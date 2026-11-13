from datetime import date

import pytest
from bson import ObjectId
from pymongo.database import Database
from pymongo.errors import OperationFailure

from reports.domain.date_range import DateRange
from reports.exceptions import DatabaseError
from reports.persistence import (
    MongoDailySummaryRepository,
    MongoInterfaceRepository,
    translate_database_errors,
)

GBPS = 1_000_000_000
RANGE = DateRange(start=date(2026, 3, 1), end=date(2026, 3, 31))


def insert_interface(
    database: Database, layer: str, name: str = "eth", status: str = "activa", **extra: object
) -> ObjectId:
    """Insert an interface and return its id."""
    document = {
        "layer": layer,
        "name": name,
        "vendor": "HUAWEI",
        "capacity_gbps": 10.0,
        "scan_url": f"http://scan/{name}/{layer}",
        "status": status,
        **extra,
    }
    return database["interfaces"].insert_one(document).inserted_id


def insert_summary(
    database: Database,
    interface_id: ObjectId,
    day: str,
    in_avg: float = 0,
    out_avg: float = 0,
    in_max: float = 0,
    out_max: float = 0,
    layer: str = "STALE",
) -> None:
    """Insert a daily summary."""
    database["traffic_summary_daily"].insert_one(
        {
            "interface_id": interface_id,
            "layer": layer,
            "date": day,
            "in_avg": in_avg,
            "out_avg": out_avg,
            "in_max": in_max,
            "out_max": out_max,
        }
    )


pytestmark = pytest.mark.integration


def test_rf034_layer_values_include_every_status_and_are_distinct(database: Database) -> None:
    """RF-034: layers come from `interfaces`, whatever the status, without repeats."""
    insert_interface(database, "BORDE", "a")
    insert_interface(database, "BORDE", "b", status="desincorporada")
    insert_interface(database, "IXP", "c", status="desincorporada")
    values = MongoInterfaceRepository(database).layer_values()
    assert sorted(values) == ["BORDE", "IXP"]


def test_rf034_interfaces_are_found_by_every_stored_variant(database: Database) -> None:
    """RF-034: interfaces are queried with the original stored values of a canonical layer."""
    insert_interface(database, "BORDE", "upper")
    insert_interface(database, "borde", "lower")
    insert_interface(database, "IXP", "other")
    found = MongoInterfaceRepository(database).find_by_layer_values(["BORDE", "borde"])
    assert sorted(interface.name for interface in found) == ["lower", "upper"]


def test_rf034_decommissioned_interfaces_are_included(database: Database) -> None:
    """RF-034: the status does not filter interfaces."""
    insert_interface(database, "BORDE", "gone", status="desincorporada")
    found = MongoInterfaceRepository(database).find_by_layer_values(["BORDE"])
    assert [interface.name for interface in found] == ["gone"]


def test_rf034_interface_data_comes_from_interfaces(database: Database) -> None:
    """RF-034: name, vendor, capacity and scan_url are read as stored."""
    interface_id = insert_interface(database, "BORDE", "eth-1", capacity_gbps=40.0)
    (interface,) = MongoInterfaceRepository(database).find_by_layer_values(["BORDE"])
    assert interface.id == interface_id
    assert (interface.name, interface.vendor, interface.capacity_gbps) == ("eth-1", "HUAWEI", 40.0)
    assert interface.scan_url == "http://scan/eth-1/BORDE"


def test_rf040_missing_vendor_and_capacity_are_empty_and_zero(database: Database) -> None:
    """RF-040: a missing vendor is read as empty and a missing capacity as 0."""
    database["interfaces"].insert_one({"layer": "BORDE", "name": "bare"})
    (interface,) = MongoInterfaceRepository(database).find_by_layer_values(["BORDE"])
    assert (interface.vendor, interface.capacity_gbps) == ("", 0.0)


def test_rf035_summaries_are_aggregated_by_interface(database: Database) -> None:
    """RF-035: average of the daily averages and maximum of the daily maximums."""
    interface_id = insert_interface(database, "BORDE")
    for day, in_avg, in_max, out_max in (
        ("2026-03-01", 2 * GBPS, 5 * GBPS, 2 * GBPS),
        ("2026-03-02", 4 * GBPS, 9 * GBPS, 3 * GBPS),
        ("2026-03-03", 6 * GBPS, 7 * GBPS, 2.5 * GBPS),
    ):
        insert_summary(database, interface_id, day, in_avg, GBPS, in_max, out_max)
    (summary,) = MongoDailySummaryRepository(database).aggregate([interface_id], RANGE)
    assert summary.interface_id == interface_id
    assert summary.in_average_bps == 4 * GBPS
    assert summary.out_average_bps == GBPS
    assert summary.in_max_bps == 9 * GBPS
    assert summary.out_max_bps == 3 * GBPS
    assert summary.days == 3


def test_rf034_range_ends_are_inclusive(database: Database) -> None:
    """RF-034: summaries on the first and last day are included, the neighbors are not."""
    interface_id = insert_interface(database, "BORDE")
    for day in ("2026-02-28", "2026-03-01", "2026-03-31", "2026-04-01"):
        insert_summary(database, interface_id, day, in_max=1)
    (summary,) = MongoDailySummaryRepository(database).aggregate([interface_id], RANGE)
    assert summary.days == 2


def test_rf034_interface_without_summaries_is_absent(database: Database) -> None:
    """RF-034: an interface without summaries in the range is not in the result."""
    with_data = insert_interface(database, "BORDE", "with")
    without_data = insert_interface(database, "BORDE", "without")
    insert_summary(database, with_data, "2026-03-05")
    insert_summary(database, without_data, "2026-04-05")
    result = MongoDailySummaryRepository(database).aggregate([with_data, without_data], RANGE)
    assert [summary.interface_id for summary in result] == [with_data]


def test_rf034_summary_layer_field_is_ignored(database: Database) -> None:
    """RF-034: membership comes from the ids of `interfaces`, not from the summary `layer`."""
    interface_id = insert_interface(database, "NEWLAYER")
    insert_summary(database, interface_id, "2026-03-05", layer="OLDLAYER")
    result = MongoDailySummaryRepository(database).aggregate([interface_id], RANGE)
    assert len(result) == 1


def test_rf034_ids_are_split_in_batches_and_combined(
    database: Database, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RF-034: a large id list is split in batches and the results are combined."""
    monkeypatch.setattr("reports.persistence.mongo_summary_repository.LOOKUP_BATCH_SIZE", 2)
    ids = [insert_interface(database, "BORDE", f"if-{number}") for number in range(5)]
    for interface_id in ids:
        insert_summary(database, interface_id, "2026-03-05", in_max=GBPS)
    repository = MongoDailySummaryRepository(database)
    assert {summary.interface_id for summary in repository.aggregate(ids, RANGE)} == set(ids)
    assert repository.dates_with_summary(ids, RANGE) == {"2026-03-05"}


def test_rf036_dates_with_summary_are_distinct_and_inside_the_range(database: Database) -> None:
    """RF-036: the days that have at least one summary in the layer."""
    first = insert_interface(database, "BORDE", "a")
    second = insert_interface(database, "BORDE", "b")
    for interface_id in (first, second):
        insert_summary(database, interface_id, "2026-03-10")
    insert_summary(database, first, "2026-03-11")
    insert_summary(database, first, "2026-05-01")
    dates = MongoDailySummaryRepository(database).dates_with_summary([first, second], RANGE)
    assert dates == {"2026-03-10", "2026-03-11"}


def test_rf031_two_runs_give_the_same_result(database: Database) -> None:
    """RF-031: aggregating twice returns identical values (deterministic accumulation)."""
    interface_id = insert_interface(database, "BORDE")
    for day, in_avg in (("2026-03-01", 0.1), ("2026-03-02", 0.2), ("2026-03-03", 0.3)):
        insert_summary(database, interface_id, day, in_avg=in_avg)
    repository = MongoDailySummaryRepository(database)
    assert repository.aggregate([interface_id], RANGE) == repository.aggregate(
        [interface_id], RANGE
    )


def test_rnf_reads_do_not_change_the_database(database: Database) -> None:
    """RNF: the repositories only read; the collections are identical afterwards."""
    interface_id = insert_interface(database, "BORDE")
    insert_summary(database, interface_id, "2026-03-05", in_avg=1, in_max=2)
    before = (
        list(database["interfaces"].find()),
        list(database["traffic_summary_daily"].find()),
        sorted(database.list_collection_names()),
    )
    MongoInterfaceRepository(database).layer_values()
    MongoInterfaceRepository(database).find_by_layer_values(["BORDE"])
    MongoDailySummaryRepository(database).aggregate([interface_id], RANGE)
    MongoDailySummaryRepository(database).dates_with_summary([interface_id], RANGE)
    after = (
        list(database["interfaces"].find()),
        list(database["traffic_summary_daily"].find()),
        sorted(database.list_collection_names()),
    )
    assert before == after


def test_rf043_database_failures_become_database_error() -> None:
    """RF-043: any PyMongo error is translated so the layer can be marked as failed."""
    with pytest.raises(DatabaseError, match="OperationFailure"), translate_database_errors():
        raise OperationFailure("boom")
