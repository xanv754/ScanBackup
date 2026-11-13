from datetime import UTC, date, datetime, timedelta

import pytest

from tests.collection.fakes import FakeStores, FakeSummaryStore, make_interface
from traffic_collector.clock import TargetDate
from traffic_collector.collection import InterfaceProcessor
from traffic_collector.constants.enums import FailureCause, SampleCountVerdict
from traffic_collector.parsing import DayFilter, LogParser, SampleValidator
from traffic_collector.scan import ScanHttpError, ScanTimeout

TARGET = TargetDate.previous_day(date(2026, 11, 6))
DAY_START = datetime(2026, 11, 5, 4, 0, tzinfo=UTC)


def build_log(
    count: int, start: datetime = DAY_START, extra: str = "", step_minutes: int = 5
) -> str:
    lines = [
        f"{int((start + timedelta(minutes=step_minutes * index)).timestamp())} 1 2 3 4"
        for index in range(count)
    ]
    return "\n".join(lines) + "\n" + extra


def build_processor(stores: FakeStores, force: bool = False) -> InterfaceProcessor:
    return InterfaceProcessor(
        target_date=TARGET,
        force=force,
        parser=LogParser(),
        day_filter=DayFilter(TARGET),
        validator=SampleValidator(),
        traffic_store=stores,
        summary_store=FakeSummaryStore(stores),
    )


@pytest.fixture
def stores() -> FakeStores:
    return FakeStores()


def test_complete_day_is_stored(stores: FakeStores) -> None:
    """288 valid samples are stored with the layer and the target date (RF-022, RF-025)."""
    result = build_processor(stores).process(make_interface(), "BORDE", build_log(288))

    assert result.succeeded
    assert result.verdict is SampleCountVerdict.COMPLETE
    assert result.sample_count == 288
    assert stores.operations == ["save"]
    assert stores.saved[0].layer == "BORDE"
    assert stores.saved[0].date == "2026-11-05"


@pytest.mark.parametrize(
    ("count", "verdict"),
    [
        (1, SampleCountVerdict.PARTIAL),
        (287, SampleCountVerdict.PARTIAL),
        (289, SampleCountVerdict.EXCESS),
    ],
)
def test_irregular_counts_are_stored_with_verdict(
    stores: FakeStores, count: int, verdict: SampleCountVerdict
) -> None:
    """1-287 and 289 samples are stored and flagged for a warning (RF-024)."""
    result = build_processor(stores).process(
        make_interface(), "BORDE", build_log(count, step_minutes=1)
    )

    assert result.succeeded
    assert result.verdict is verdict
    assert len(stores.saved[0].samples) == count


def test_zero_valid_samples_fail_without_storing(stores: FakeStores) -> None:
    """Zero valid samples of the day fail the interface and store nothing (RF-024)."""
    other_day = build_log(10, start=DAY_START - timedelta(days=3))

    result = build_processor(stores).process(make_interface(), "BORDE", other_day)

    assert not result.succeeded
    assert result.cause is FailureCause.NO_VALID_SAMPLES
    assert stores.operations == []


def test_samples_of_other_days_are_discarded(stores: FakeStores) -> None:
    """Only the samples of the target day are stored (RF-023)."""
    log = build_log(288) + build_log(50, start=DAY_START + timedelta(days=1))

    result = build_processor(stores).process(make_interface(), "BORDE", log)

    assert result.sample_count == 288


def test_invalid_lines_are_counted_and_do_not_fail(stores: FakeStores) -> None:
    """Invalid lines are discarded and counted, the rest is stored (RF-023)."""
    result = build_processor(stores).process(
        make_interface(), "BORDE", build_log(288, extra="garbage\nmore garbage\n")
    )

    assert result.succeeded
    assert result.invalid_line_count == 2


def test_only_invalid_lines_fail_the_interface(stores: FakeStores) -> None:
    """A log with no valid line has zero valid samples (RF-024)."""
    result = build_processor(stores).process(make_interface(), "BORDE", "garbage\n")

    assert result.cause is FailureCause.NO_VALID_SAMPLES
    assert result.invalid_line_count == 1


@pytest.mark.parametrize("force", [False, True])
def test_scan_error_fails_with_its_cause_and_touches_nothing(
    stores: FakeStores, force: bool
) -> None:
    """A download error fails the interface; nothing is deleted or stored (RF-021, RF-022)."""
    processor = build_processor(stores, force=force)

    timeout = processor.process(make_interface(), "BORDE", ScanTimeout())
    http = processor.process(make_interface(), "BORDE", ScanHttpError(500))

    assert timeout.cause is FailureCause.TIMEOUT
    assert http.cause is FailureCause.HTTP_ERROR
    assert stores.operations == []


def test_force_with_zero_valid_samples_deletes_nothing(stores: FakeStores) -> None:
    """--force never deletes when the new data is not valid (RF-021)."""
    result = build_processor(stores, force=True).process(
        make_interface(), "BORDE", "garbage"
    )

    assert not result.succeeded
    assert stores.operations == []


def test_force_deletes_summary_then_raw_then_saves(stores: FakeStores) -> None:
    """--force deletes the summary, then the raw day, then stores the new one (RF-021)."""
    result = build_processor(stores, force=True).process(
        make_interface(), "BORDE", build_log(288)
    )

    assert result.succeeded
    assert stores.operations == ["delete_summary", "delete", "save"]


def test_without_force_nothing_is_deleted(stores: FakeStores) -> None:
    """Without --force the service never deletes data (RF-021)."""
    build_processor(stores).process(make_interface(), "BORDE", build_log(288))

    assert "delete" not in stores.operations
    assert "delete_summary" not in stores.operations


def test_database_error_on_save_is_a_storage_failure(stores: FakeStores) -> None:
    """A database error while storing fails the interface and cuts the layer (RF-025, RF-027)."""
    stores.fail_on = "save"

    result = build_processor(stores).process(make_interface(), "BORDE", build_log(288))

    assert result.cause is FailureCause.STORAGE_ERROR
    assert result.is_storage_failure


@pytest.mark.parametrize("failing_operation", ["delete_summary", "delete"])
def test_database_error_on_forced_delete_does_not_save(
    stores: FakeStores, failing_operation: str
) -> None:
    """If a forced deletion fails, nothing new is saved (RF-021, RF-025)."""
    stores.fail_on = failing_operation

    result = build_processor(stores, force=True).process(
        make_interface(), "BORDE", build_log(288)
    )

    assert result.is_storage_failure
    assert stores.saved == []
