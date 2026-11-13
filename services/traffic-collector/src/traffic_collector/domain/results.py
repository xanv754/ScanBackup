from dataclasses import dataclass

from traffic_collector.constants.enums import (
    CutReason,
    ExitCode,
    FailureCause,
    SampleCountVerdict,
)
from traffic_collector.domain.models import ActiveInterface


@dataclass(frozen=True, slots=True)
class InterfaceResult:
    """What happened with one interface [RF-022].

    A successful result carries the sample verdict and the invalid lines found, so the
    reporter can warn about them. A failed result carries the cause.
    """

    interface: ActiveInterface
    cause: FailureCause | None = None
    sample_count: int = 0
    verdict: SampleCountVerdict | None = None
    invalid_line_count: int = 0

    @property
    def succeeded(self) -> bool:
        """Return True if the interface was stored."""
        return self.cause is None

    @property
    def is_storage_failure(self) -> bool:
        """Return True if the failure came from the database and must cut the layer [RF-027]."""
        return self.cause is FailureCause.STORAGE_ERROR


@dataclass(frozen=True, slots=True)
class LayerResult:
    """The outcome of one layer [RF-027].

    A layer fails if any interface failed, if it was cut or if it could not be read. Skipped
    interfaces never count as failures and an empty layer is successful.
    """

    layer: str
    active_count: int = 0
    skipped_count: int = 0
    stored_count: int = 0
    failed_count: int = 0
    not_processed_count: int = 0
    cut_reason: CutReason | None = None
    read_failed: bool = False

    @property
    def failed(self) -> bool:
        """Return True if the layer is failed."""
        return self.failed_count > 0 or self.cut_reason is not None or self.read_failed

    @property
    def has_active_interfaces(self) -> bool:
        """Return True if the layer had at least one active interface."""
        return self.active_count > 0


@dataclass(frozen=True, slots=True)
class SummaryResult:
    """The outcome of the daily summary phase [RF-026]."""

    failed_count: int = 0

    @property
    def failed(self) -> bool:
        """Return True if the summary of any interface failed."""
        return self.failed_count > 0


@dataclass(frozen=True, slots=True)
class RunResult:
    """The overall outcome of the run [RF-028].

    It is failed if any layer failed, if the summary failed, or if no layer had active
    interfaces. A rerun where everything is skipped is successful.
    """

    layers: tuple[LayerResult, ...]
    summary: SummaryResult

    @property
    def failed(self) -> bool:
        """Return True if the overall result is failed."""
        return (
            any(layer.failed for layer in self.layers)
            or self.summary.failed
            or not any(layer.has_active_interfaces for layer in self.layers)
        )

    @property
    def exit_code(self) -> ExitCode:
        """Return `SUCCESS` for a successful run and `FAILED` otherwise."""
        return ExitCode.FAILED if self.failed else ExitCode.SUCCESS
