import threading
import time
from collections.abc import Callable

from bson import ObjectId

from traffic_collector.domain import ActiveInterface, DailyTraffic
from traffic_collector.exceptions import DatabaseError
from traffic_collector.reporting.events import Event
from traffic_collector.scan import ScanError

type Behavior = str | ScanError | Callable[[], str | ScanError]


class FakeStores:
    """In-memory TrafficStore that records the order of operations and can fail on demand."""

    def __init__(self) -> None:
        self.operations: list[str] = []
        self.saved: list[DailyTraffic] = []
        self.fail_on: str | None = None
        self.collected_ids: set[ObjectId] = set()
        self.collected_queries = 0
        self.fail_on_nth_save: int | None = None

    def interface_ids_with_samples(self, layer: str, date: str) -> set[ObjectId]:
        if self.fail_on == "collected":
            raise DatabaseError("collected")
        self.collected_queries += 1
        return self.collected_ids

    def save(self, daily_traffic: DailyTraffic) -> None:
        self._record("save")
        if self.fail_on_nth_save is not None and len(self.saved) + 1 == self.fail_on_nth_save:
            raise DatabaseError("save")
        self.saved.append(daily_traffic)

    def delete_day(self, interface_id: ObjectId, date: str) -> None:
        self._record("delete")

    def _record(self, operation: str) -> None:
        if self.fail_on == operation:
            raise DatabaseError(operation)
        self.operations.append(operation)


class FakeSummaryStore:
    """SummaryStore that records its deletions in the shared operation list."""

    def __init__(self, stores: FakeStores) -> None:
        self._stores = stores

    def delete_day(self, interface_id: ObjectId, date: str) -> None:
        if self._stores.fail_on == "delete_summary":
            raise DatabaseError("delete_summary")
        self._stores.operations.append("delete_summary")


class FakeInterfaceReader:
    """InterfaceReader with fixed layers and a failure switch."""

    def __init__(self, interfaces_by_layer: dict[str, list[ActiveInterface]]) -> None:
        self._interfaces_by_layer = interfaces_by_layer
        self.fail = False
        self.fail_layers = False

    def layers(self) -> list[str]:
        if self.fail_layers:
            raise DatabaseError("layers")
        return sorted(self._interfaces_by_layer)

    def active_by_layer(self, layer: str) -> list[ActiveInterface]:
        if self.fail:
            raise DatabaseError("interfaces")
        return self._interfaces_by_layer.get(layer, [])


class FakeScanClient:
    """ScanClient with one behavior per URL; records calls and the peak of parallel downloads.

    A behavior is the log text, a `ScanError` to raise, or a callable returning one of them.
    """

    def __init__(
        self,
        behaviors: dict[str, Behavior],
        delay_seconds: float = 0.0,
    ) -> None:
        self._behaviors = behaviors
        self._delay_seconds = delay_seconds
        self._lock = threading.Lock()
        self._running = 0
        self.peak_parallel = 0
        self.fetched: list[str] = []

    def fetch(self, scan_url: str) -> str:
        with self._lock:
            self._running += 1
            self.peak_parallel = max(self.peak_parallel, self._running)
            self.fetched.append(scan_url)
        try:
            time.sleep(self._delay_seconds)
            behavior = self._behaviors[scan_url]
            outcome = behavior() if callable(behavior) else behavior
            if isinstance(outcome, ScanError):
                raise outcome
            return outcome
        finally:
            with self._lock:
                self._running -= 1


class RecordingSink:
    """EventSink that keeps every published event."""

    def __init__(self) -> None:
        self.events: list[Event] = []

    def publish(self, event: Event) -> None:
        self.events.append(event)

    def of_type(self, event_type: type) -> list[Event]:
        return [event for event in self.events if isinstance(event, event_type)]


def make_interface(url: str = "https://scan/x.log") -> ActiveInterface:
    return ActiveInterface(interface_id=ObjectId(), scan_url=url)
