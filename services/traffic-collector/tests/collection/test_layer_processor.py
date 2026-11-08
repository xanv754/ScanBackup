import time
from datetime import UTC, date, datetime, timedelta

from tests.collection.fakes import (
    Behavior,
    FakeInterfaceReader,
    FakeScanClient,
    FakeStores,
    FakeSummaryStore,
    RecordingSink,
    make_interface,
)
from traffic_collector.clock import TargetDate
from traffic_collector.collection import InterfaceProcessor, LayerProcessor
from traffic_collector.constants.enums import CutReason, FailureCause
from traffic_collector.domain.results import LayerResult
from traffic_collector.parsing import DayFilter, LogParser, SampleValidator
from traffic_collector.reporting.events import (
    InterfaceFailed,
    LayerCut,
    LayerEmpty,
    LayerReadFailed,
    LayerStarted,
)
from traffic_collector.scan import ScanTimeout
from traffic_collector.settings import CollectionConfig

TARGET = TargetDate.previous_day(date(2026, 11, 6))
LAYER = "BORDE"
GOOD_LOG = f"{int(datetime(2026, 11, 5, 4, 0, tzinfo=UTC).timestamp())} 1 2 3 4\n"
GOOD_LOG_LATER = (
    f"{int((datetime(2026, 11, 5, 4, 0, tzinfo=UTC) + timedelta(minutes=5)).timestamp())} 1 2 3 4\n"
)


class Scenario:
    """Wires a LayerProcessor with fakes for one test."""

    def __init__(
        self,
        behaviors: list[Behavior],
        max_concurrent_requests: int = 1,
        max_consecutive_failures: int = 3,
        force: bool = False,
        delay_seconds: float = 0.0,
    ) -> None:
        self.interfaces = [make_interface(f"https://scan/{i}.log") for i in range(len(behaviors))]
        self.stores = FakeStores()
        self.reader = FakeInterfaceReader({LAYER: self.interfaces})
        self.scan_client = FakeScanClient(
            {
                item.scan_url: behavior
                for item, behavior in zip(self.interfaces, behaviors, strict=True)
            },
            delay_seconds=delay_seconds,
        )
        self.sink = RecordingSink()
        interface_processor = InterfaceProcessor(
            target_date=TARGET,
            force=force,
            parser=LogParser(),
            day_filter=DayFilter(TARGET),
            validator=SampleValidator(),
            traffic_store=self.stores,
            summary_store=FakeSummaryStore(self.stores),
        )
        self.processor = LayerProcessor(
            target_date=TARGET,
            force=force,
            config=CollectionConfig(
                max_concurrent_requests=max_concurrent_requests,
                request_timeout_seconds=30,
                max_consecutive_failures=max_consecutive_failures,
            ),
            interface_reader=self.reader,
            traffic_store=self.stores,
            scan_client=self.scan_client,
            interface_processor=interface_processor,
            event_sink=self.sink,
        )

    def run(self) -> LayerResult:
        return self.processor.process(LAYER)


def failing() -> ScanTimeout:
    return ScanTimeout()


def slow_good_log() -> str:
    """A valid log that arrives after the fast failures."""
    time.sleep(0.3)
    return GOOD_LOG


def test_layer_without_active_interfaces_is_successful_with_warning() -> None:
    """An empty layer warns and is successful, with no SCAN request (RF-019)."""
    scenario = Scenario([])

    result = scenario.run()

    assert not result.failed
    assert not result.has_active_interfaces
    assert len(scenario.sink.of_type(LayerEmpty)) == 1
    assert scenario.scan_client.fetched == []


def test_all_interfaces_stored_is_a_successful_layer() -> None:
    """A layer where every interface is stored is successful (RF-027)."""
    scenario = Scenario([GOOD_LOG] * 4, max_concurrent_requests=2)

    result = scenario.run()

    assert not result.failed
    assert result.stored_count == 4
    assert len(scenario.stores.saved) == 4


def test_collected_interfaces_are_skipped_with_one_query() -> None:
    """Interfaces with samples are skipped, using one query for the layer (RF-020)."""
    scenario = Scenario([GOOD_LOG] * 3)
    scenario.stores.collected_ids = {scenario.interfaces[0].interface_id}

    result = scenario.run()

    assert result.skipped_count == 1
    assert result.stored_count == 2
    assert scenario.stores.collected_queries == 1
    assert scenario.interfaces[0].scan_url not in scenario.scan_client.fetched


def test_layer_with_everything_skipped_is_successful_without_requests() -> None:
    """A fully collected layer is successful and does not query SCAN (RF-020)."""
    scenario = Scenario([GOOD_LOG] * 3)
    scenario.stores.collected_ids = {item.interface_id for item in scenario.interfaces}

    result = scenario.run()

    assert not result.failed
    assert result.skipped_count == 3
    assert scenario.scan_client.fetched == []


def test_force_ignores_the_skip_and_does_not_query_it() -> None:
    """With --force every active interface is collected and no skip query is made (RF-021)."""
    scenario = Scenario([GOOD_LOG] * 3, force=True)
    scenario.stores.collected_ids = {item.interface_id for item in scenario.interfaces}

    result = scenario.run()

    assert result.skipped_count == 0
    assert result.stored_count == 3
    assert scenario.stores.collected_queries == 0


def test_consecutive_failures_cut_the_layer_and_keep_what_was_stored() -> None:
    """The threshold of consecutive failures cuts the layer; stored data is kept (RF-027)."""
    scenario = Scenario([GOOD_LOG, failing(), failing(), failing(), GOOD_LOG, GOOD_LOG])

    result = scenario.run()

    assert result.failed
    assert result.cut_reason is CutReason.CONSECUTIVE_FAILURES
    assert result.stored_count == 1
    assert result.failed_count == 3
    assert result.not_processed_count == 2
    assert len(scenario.stores.saved) == 1
    assert len(scenario.scan_client.fetched) == 4
    assert [event.reason for event in scenario.sink.of_type(LayerCut)] == [
        CutReason.CONSECUTIVE_FAILURES
    ]


def test_a_success_resets_the_consecutive_failure_count() -> None:
    """Failures separated by a success never reach the threshold (RF-027)."""
    behaviors = [failing(), failing(), GOOD_LOG, failing(), failing(), GOOD_LOG, failing()]
    scenario = Scenario(behaviors)

    result = scenario.run()

    assert result.cut_reason is None
    assert result.failed
    assert result.failed_count == 5
    assert result.stored_count == 2
    assert result.not_processed_count == 0


def test_layer_with_a_failed_interface_is_failed_even_if_all_were_processed() -> None:
    """One failed interface makes the layer failed (RF-027)."""
    scenario = Scenario([GOOD_LOG, failing(), GOOD_LOG])

    result = scenario.run()

    assert result.failed
    assert result.cut_reason is None
    assert result.not_processed_count == 0
    failures = scenario.sink.of_type(InterfaceFailed)
    assert [event.cause for event in failures] == [FailureCause.TIMEOUT]


def test_storage_error_cuts_the_layer_and_keeps_what_was_stored() -> None:
    """A database error while storing cuts the layer at once (RF-025, RF-027)."""
    scenario = Scenario([GOOD_LOG, GOOD_LOG_LATER, GOOD_LOG, GOOD_LOG])
    scenario.stores.fail_on_nth_save = 3

    result = scenario.run()

    assert result.cut_reason is CutReason.STORAGE_ERROR
    assert result.stored_count == 2
    assert len(scenario.stores.saved) == 2
    assert result.not_processed_count == 1


def test_downloads_after_the_cut_are_discarded_not_stored() -> None:
    """What finishes downloading after the cut is thrown away (RF-027)."""
    scenario = Scenario(
        [failing(), failing(), slow_good_log, slow_good_log],
        max_concurrent_requests=4,
        max_consecutive_failures=2,
    )

    result = scenario.run()

    assert result.cut_reason is CutReason.CONSECUTIVE_FAILURES
    assert result.stored_count == 0
    assert scenario.stores.saved == []
    assert result.not_processed_count == 2


def test_requests_in_flight_never_exceed_the_limit() -> None:
    """Never more than max_concurrent_requests downloads at once (RF-016)."""
    scenario = Scenario([GOOD_LOG] * 30, max_concurrent_requests=4, delay_seconds=0.02)

    result = scenario.run()

    assert result.stored_count == 30
    assert 1 < scenario.scan_client.peak_parallel <= 4


def test_layer_read_failure_fails_the_layer_without_raising() -> None:
    """A database error reading the layer makes it failed, not the process crash."""
    scenario = Scenario([GOOD_LOG])
    scenario.reader.fail = True

    result = scenario.run()

    assert result.failed
    assert result.read_failed
    assert len(scenario.sink.of_type(LayerReadFailed)) == 1
    assert scenario.scan_client.fetched == []


def test_skip_query_failure_fails_the_layer_without_requests() -> None:
    """A database error in the skip query fails the layer and queries nothing in SCAN."""
    scenario = Scenario([GOOD_LOG])
    scenario.stores.fail_on = "collected"

    result = scenario.run()

    assert result.read_failed
    assert scenario.scan_client.fetched == []


def test_layer_started_event_reports_counts() -> None:
    """The layer start announces active and skipped interfaces (RF-030)."""
    scenario = Scenario([GOOD_LOG] * 3)
    scenario.stores.collected_ids = {scenario.interfaces[0].interface_id}

    scenario.run()

    started = scenario.sink.of_type(LayerStarted)[0]
    assert (started.active_count, started.skipped_count) == (3, 1)
