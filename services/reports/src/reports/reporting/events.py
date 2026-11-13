from abc import ABC, abstractmethod
from dataclasses import dataclass

from reports.domain.date_range import DateRange
from reports.domain.results import ExportSummary, LayerResult, RunResult


@dataclass(frozen=True, slots=True)
class RunStarted:
    """The run starts with a valid range [RF-045]."""

    date_range: DateRange


@dataclass(frozen=True, slots=True)
class ProcessFailed:
    """General error of the process; one cause per entry [RF-044]."""

    causes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class LayerEmpty:
    """A layer has no interface with summaries in the range, so it gets no sheet [RF-043]."""

    layer: str


@dataclass(frozen=True, slots=True)
class LayerFailed:
    """A layer failed and is skipped; the run continues with the next one [RF-043]."""

    layer: str
    cause: str


@dataclass(frozen=True, slots=True)
class LayerIncomplete:
    """Interfaces of a layer have fewer summaries than the days of the range [RF-036]."""

    layer: str
    interface_count: int


@dataclass(frozen=True, slots=True)
class LayerFinished:
    """A layer was processed, with or without success [RF-043]."""

    result: LayerResult


@dataclass(frozen=True, slots=True)
class MissingDay:
    """A day of the range has no summaries in any successfully processed layer [RF-036]."""

    day: str


@dataclass(frozen=True, slots=True)
class FileGenerated:
    """The report file was written [RF-042]."""

    summary: ExportSummary


@dataclass(frozen=True, slots=True)
class ExportFailed:
    """The report file could not be written [RF-042]."""

    cause: str


@dataclass(frozen=True, slots=True)
class RunFinished:
    """The overall result of the run [RF-044]."""

    result: RunResult


Event = (
    RunStarted
    | ProcessFailed
    | LayerEmpty
    | LayerFailed
    | LayerIncomplete
    | LayerFinished
    | MissingDay
    | FileGenerated
    | ExportFailed
    | RunFinished
)


class EventSink(ABC):
    """Receives the events of the run. The processing never writes text itself."""

    @abstractmethod
    def publish(self, event: Event) -> None:
        """Handle an event of the run."""
