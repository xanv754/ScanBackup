from collections.abc import Iterator
from typing import Protocol

from bson import ObjectId

from traffic_collector.clock import TargetDate
from traffic_collector.domain import ActiveInterface, DailySummary, DailyTraffic
from traffic_collector.domain.results import LayerResult, SummaryResult


class InterfaceReader(Protocol):
    """Read access to the interfaces."""

    def layers(self) -> list[str]:
        """Return the layers in ascending order."""
        ...

    def active_by_layer(self, layer: str) -> list[ActiveInterface]:
        """Return the active interfaces of a layer with a single query."""
        ...


class TrafficStore(Protocol):
    """Storage of the raw traffic of a day."""

    def interface_ids_with_samples(self, layer: str, date: str) -> set[ObjectId]:
        """Return the interfaces of a layer that already have samples on a date."""
        ...

    def save(self, daily_traffic: DailyTraffic) -> None:
        """Store the day of an interface (idempotent)."""
        ...

    def delete_day(self, interface_id: ObjectId, date: str) -> None:
        """Delete the raw document of an interface for a date."""
        ...


class SummaryStore(Protocol):
    """Deletion of daily summaries."""

    def delete_day(self, interface_id: ObjectId, date: str) -> None:
        """Delete the summary of an interface for a date."""
        ...


class TrafficReader(Protocol):
    """Read access to the raw traffic of a day."""

    def daily_by_date(self, date: str) -> Iterator[DailyTraffic]:
        """Stream the stored days of every interface on a date."""
        ...


class SummaryWriter(Protocol):
    """Storage of the daily summaries."""

    def interface_ids_with_summary(self, date: str) -> set[ObjectId]:
        """Return the interfaces that already have a summary on a date."""
        ...

    def save(self, summary: DailySummary) -> None:
        """Store the summary of an interface (idempotent)."""
        ...


class LayerCollector(Protocol):
    """Collects all the interfaces of one layer."""

    def process(self, layer: str) -> LayerResult:
        """Process a layer and return its result."""
        ...


class SummaryPhase(Protocol):
    """Daily summary [RF-026], run once after all the layers."""

    def run(self, target_date: TargetDate) -> SummaryResult:
        """Generate the daily summary of `target_date` and return its result."""
        ...
