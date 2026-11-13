from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

from bson import ObjectId

from reports.clock import Clock
from reports.domain.date_range import DateRange
from reports.domain.models import AggregatedSummary, InterfaceInfo, LayerData
from reports.exceptions import DatabaseError, ExportError, InvalidSheetNameError
from reports.export import ReportExporter
from reports.persistence import DailySummaryRepository, InterfaceRepository
from reports.reporting import Event, EventSink


class FixedClock(Clock):
    """Clock that always returns the moment it was built with."""

    def __init__(self, moment: datetime) -> None:
        """Receive the timezone-aware moment to return."""
        self._moment = moment

    def now(self) -> datetime:
        return self._moment


class FakeInterfaceRepository(InterfaceRepository):
    """In-memory interfaces by stored layer value, with switches to make the database fail."""

    def __init__(
        self,
        interfaces_by_layer: dict[str, list[InterfaceInfo]],
        fail_layer_values: bool = False,
        failing_layers: frozenset[str] = frozenset(),
    ) -> None:
        """Receive the interfaces of each stored layer value and what must fail."""
        self._interfaces_by_layer = interfaces_by_layer
        self._fail_layer_values = fail_layer_values
        self._failing_layers = failing_layers
        self.queried_layers: list[tuple[str, ...]] = []

    def layer_values(self) -> list[str]:
        if self._fail_layer_values:
            raise DatabaseError("ServerSelectionTimeoutError")
        return list(self._interfaces_by_layer)

    def find_by_layer_values(self, stored_values: Sequence[str]) -> list[InterfaceInfo]:
        self.queried_layers.append(tuple(stored_values))
        if any(value in self._failing_layers for value in stored_values):
            raise DatabaseError("OperationFailure")
        return [
            interface
            for value in stored_values
            for interface in self._interfaces_by_layer.get(value, [])
        ]


class FakeDailySummaryRepository(DailySummaryRepository):
    """In-memory aggregated summaries, with the days that have summaries per interface."""

    def __init__(
        self,
        summaries: list[AggregatedSummary],
        days_by_interface: dict[ObjectId, set[str]] | None = None,
        failing_interfaces: frozenset[ObjectId] = frozenset(),
    ) -> None:
        """Receive the aggregated summaries and the interfaces whose read must fail."""
        self._summaries = summaries
        self._days_by_interface = days_by_interface or {}
        self._failing_interfaces = failing_interfaces

    def aggregate(
        self, interface_ids: Sequence[ObjectId], date_range: DateRange
    ) -> list[AggregatedSummary]:
        self._fail_if_needed(interface_ids)
        return [
            summary
            for summary in self._summaries
            if summary.interface_id in interface_ids
        ]

    def dates_with_summary(
        self, interface_ids: Sequence[ObjectId], date_range: DateRange
    ) -> set[str]:
        self._fail_if_needed(interface_ids)
        return set().union(
            *(self._days_by_interface.get(id_, set()) for id_ in interface_ids)
        )

    def _fail_if_needed(self, interface_ids: Sequence[ObjectId]) -> None:
        """Raise `DatabaseError` if any requested interface is configured to fail."""
        if any(
            interface_id in self._failing_interfaces for interface_id in interface_ids
        ):
            raise DatabaseError("OperationFailure")


class FakeExporter(ReportExporter):
    """Records the layers it receives and the files it would write."""

    def __init__(
        self,
        invalid_layer_names: frozenset[str] = frozenset(),
        fail_on_save: bool = False,
    ) -> None:
        """Receive the layer names to reject and whether saving must fail."""
        self._invalid_layer_names = invalid_layer_names
        self._fail_on_save = fail_on_save
        self.layers: list[LayerData] = []
        self.saved_paths: list[Path] = []

    @property
    def file_extension(self) -> str:
        return ".fake"

    def validate_layer_name(self, layer_name: str) -> None:
        if layer_name in self._invalid_layer_names:
            raise InvalidSheetNameError("nombre inválido")

    def add_layer(self, data: LayerData) -> None:
        self.layers.append(data)

    def save(self, destination: Path) -> None:
        if self._fail_on_save:
            raise ExportError("disco lleno")
        self.saved_paths.append(destination)


class RecordingSink(EventSink):
    """Keeps every published event."""

    def __init__(self) -> None:
        """Start with no events."""
        self.events: list[Event] = []

    def publish(self, event: Event) -> None:
        self.events.append(event)

    def of_type[EventT](self, event_type: type[EventT]) -> list[EventT]:
        """Return the events of a type, in publication order."""
        return [event for event in self.events if isinstance(event, event_type)]
