from dataclasses import dataclass
from typing import Protocol

from traffic_collector.constants.enums import (
    CutReason,
    FailureCause,
    SampleCountVerdict,
)
from traffic_collector.domain import ActiveInterface
from traffic_collector.domain.results import LayerResult, RunResult


@dataclass(frozen=True, slots=True)
class LayerStarted:
    """A layer starts: how many active interfaces it has and how many are skipped [RF-020]."""

    layer: str
    active_count: int
    skipped_count: int


@dataclass(frozen=True, slots=True)
class LayerEmpty:
    """A layer has no active interfaces (warning) [RF-019]."""

    layer: str


@dataclass(frozen=True, slots=True)
class LayerReadFailed:
    """The interfaces or the stored days of a layer could not be read (error)."""

    layer: str


@dataclass(frozen=True, slots=True)
class InterfaceFailed:
    """An interface failed with a cause (error) [RF-022]."""

    layer: str
    interface: ActiveInterface
    cause: FailureCause


@dataclass(frozen=True, slots=True)
class InterfaceSampleCountWarning:
    """An interface was stored with a number of samples other than 288 (warning) [RF-024]."""

    layer: str
    interface: ActiveInterface
    verdict: SampleCountVerdict
    sample_count: int


@dataclass(frozen=True, slots=True)
class InterfaceInvalidLines:
    """Invalid lines were discarded from the log of an interface (warning) [RF-023]."""

    layer: str
    interface: ActiveInterface
    line_count: int


@dataclass(frozen=True, slots=True)
class LayerCut:
    """The processing of a layer was cut (error) [RF-027]."""

    layer: str
    reason: CutReason
    not_processed_count: int


@dataclass(frozen=True, slots=True)
class LayerFinished:
    """A layer finished with its result [RF-019]."""

    result: LayerResult


@dataclass(frozen=True, slots=True)
class SummaryFinished:
    """The daily summary finished: summaries written and interfaces skipped [RF-026]."""

    generated_count: int
    skipped_count: int


@dataclass(frozen=True, slots=True)
class SummaryFailed:
    """The daily summary stopped by a database error (error) [RF-026]."""

    generated_count: int
    error: BaseException


@dataclass(frozen=True, slots=True)
class RunFinished:
    """The run finished with its overall result [RF-028]."""

    result: RunResult


@dataclass(frozen=True, slots=True)
class ProcessFailed:
    """A general error of the process: nothing was collected (error) [RF-028].

    `error` is set for unexpected exceptions so the logger can keep their traceback.
    """

    causes: tuple[str, ...]
    error: BaseException | None = None


type Event = (
    LayerStarted
    | LayerEmpty
    | LayerReadFailed
    | InterfaceFailed
    | InterfaceSampleCountWarning
    | InterfaceInvalidLines
    | LayerCut
    | LayerFinished
    | SummaryFinished
    | SummaryFailed
    | RunFinished
    | ProcessFailed
)


class EventSink(Protocol):
    """Receives the events of the run. Processing never writes text itself."""

    def publish(self, event: Event) -> None:
        """Deliver one event."""
        ...
