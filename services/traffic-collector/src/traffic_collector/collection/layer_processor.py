from collections.abc import Iterator
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait

from traffic_collector.clock import TargetDate
from traffic_collector.collection.interface_processor import InterfaceProcessor
from traffic_collector.collection.protocols import InterfaceReader, TrafficStore
from traffic_collector.constants.enums import CutReason, SampleCountVerdict
from traffic_collector.domain import ActiveInterface
from traffic_collector.domain.results import InterfaceResult, LayerResult
from traffic_collector.exceptions import DatabaseError
from traffic_collector.reporting.events import (
    EventSink,
    InterfaceFailed,
    InterfaceInvalidLines,
    InterfaceSampleCountWarning,
    LayerCut,
    LayerEmpty,
    LayerReadFailed,
    LayerStarted,
)
from traffic_collector.scan import ScanClient, ScanError
from traffic_collector.settings import CollectionConfig


class LayerProcessor:
    """Collects all the active interfaces of one layer [RF-019, RF-020, RF-027].

    Worker threads only download. The calling thread processes every download in the order
    in which they finish, so the cut is decided in a single place without race conditions and
    anything downloaded after the cut is discarded without being stored.
    """

    def __init__(
        self,
        target_date: TargetDate,
        force: bool,
        config: CollectionConfig,
        interface_reader: InterfaceReader,
        traffic_store: TrafficStore,
        scan_client: ScanClient,
        interface_processor: InterfaceProcessor,
        event_sink: EventSink,
    ) -> None:
        """Receive the day, the force flag, the limits and every collaborator."""
        self._target_date = target_date
        self._force = force
        self._config = config
        self._interface_reader = interface_reader
        self._traffic_store = traffic_store
        self._scan_client = scan_client
        self._interface_processor = interface_processor
        self._event_sink = event_sink

    def process(self, layer: str) -> LayerResult:
        """Process one layer and return its result.

        An empty layer is successful (warning). A database error while reading the layer makes
        it failed. What was stored before a cut is kept.
        """
        try:
            active_interfaces = self._interface_reader.active_by_layer(layer)
            if not active_interfaces:
                self._event_sink.publish(LayerEmpty(layer))
                return LayerResult(layer=layer)
            pending_interfaces = self._exclude_collected(layer, active_interfaces)
        except DatabaseError:
            self._event_sink.publish(LayerReadFailed(layer))
            return LayerResult(layer=layer, read_failed=True)

        skipped_count = len(active_interfaces) - len(pending_interfaces)
        self._event_sink.publish(LayerStarted(layer, len(active_interfaces), skipped_count))
        return self._collect(layer, len(active_interfaces), skipped_count, pending_interfaces)

    def _exclude_collected(
        self, layer: str, active_interfaces: list[ActiveInterface]
    ) -> list[ActiveInterface]:
        """Return the interfaces without samples of the day, using one query [RF-020].

        With `force` nothing is skipped and the query is not made.
        """
        if self._force:
            return active_interfaces
        collected_ids = self._traffic_store.interface_ids_with_samples(layer, self._target_date.key)
        return [item for item in active_interfaces if item.interface_id not in collected_ids]

    def _collect(
        self,
        layer: str,
        active_count: int,
        skipped_count: int,
        pending_interfaces: list[ActiveInterface],
    ) -> LayerResult:
        """Download with a bounded window and process each download as it arrives."""
        stored_count = 0
        failed_count = 0
        processed_count = 0
        consecutive_failures = 0
        cut_reason: CutReason | None = None
        remaining = iter(pending_interfaces)
        in_flight: dict[Future[str | ScanError], ActiveInterface] = {}

        with ThreadPoolExecutor(max_workers=self._config.max_concurrent_requests) as pool:
            self._fill_window(pool, remaining, in_flight)
            while in_flight:
                finished, _ = wait(in_flight, return_when=FIRST_COMPLETED)
                for future in finished:
                    interface = in_flight.pop(future)
                    if cut_reason is not None:
                        continue
                    result = self._interface_processor.process(interface, layer, future.result())
                    processed_count += 1
                    self._report(layer, result)
                    if result.succeeded:
                        stored_count += 1
                        consecutive_failures = 0
                        continue
                    failed_count += 1
                    consecutive_failures += 1
                    cut_reason = self._cut_reason(result, consecutive_failures)
                    if cut_reason is not None:
                        for pending_future in in_flight:
                            pending_future.cancel()
                if cut_reason is None:
                    self._fill_window(pool, remaining, in_flight)

        not_processed_count = len(pending_interfaces) - processed_count
        if cut_reason is not None:
            self._event_sink.publish(LayerCut(layer, cut_reason, not_processed_count))
        return LayerResult(
            layer=layer,
            active_count=active_count,
            skipped_count=skipped_count,
            stored_count=stored_count,
            failed_count=failed_count,
            not_processed_count=not_processed_count,
            cut_reason=cut_reason,
        )

    def _fill_window(
        self,
        pool: ThreadPoolExecutor,
        remaining: Iterator[ActiveInterface],
        in_flight: dict[Future[str | ScanError], ActiveInterface],
    ) -> None:
        """Submit downloads until `max_concurrent_requests` are in flight or none remain."""
        while len(in_flight) < self._config.max_concurrent_requests:
            interface = next(remaining, None)
            if interface is None:
                return
            in_flight[pool.submit(self._download, interface.scan_url)] = interface

    def _download(self, scan_url: str) -> str | ScanError:
        """Download in a worker thread; a SCAN failure is returned, not raised."""
        try:
            return self._scan_client.fetch(scan_url)
        except ScanError as error:
            return error

    def _cut_reason(self, result: InterfaceResult, consecutive_failures: int) -> CutReason | None:
        """Return why the layer must be cut after a failed interface, or None to continue."""
        if result.is_storage_failure:
            return CutReason.STORAGE_ERROR
        if consecutive_failures >= self._config.max_consecutive_failures:
            return CutReason.CONSECUTIVE_FAILURES
        return None

    def _report(self, layer: str, result: InterfaceResult) -> None:
        """Publish the events that an interface result produces."""
        if result.cause is not None:
            self._event_sink.publish(InterfaceFailed(layer, result.interface, result.cause))
        elif result.verdict not in (SampleCountVerdict.COMPLETE, None):
            self._event_sink.publish(
                InterfaceSampleCountWarning(
                    layer, result.interface, result.verdict, result.sample_count
                )
            )
        if result.invalid_line_count:
            self._event_sink.publish(
                InterfaceInvalidLines(layer, result.interface, result.invalid_line_count)
            )
