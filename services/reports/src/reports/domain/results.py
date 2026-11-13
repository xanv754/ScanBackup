from dataclasses import dataclass, field
from pathlib import Path

from reports.constants.enums import ExitCode
from reports.domain.models import LayerData


@dataclass(frozen=True, slots=True)
class LayerResult:
    """Result of processing one layer [RF-043].

    A layer is failed when it carries a `failure_cause`. A successful layer without included
    interfaces is valid: it only gets a warning and no sheet.
    """

    layer: str
    included_count: int = 0
    incomplete_count: int = 0
    dates_with_summary: frozenset[str] = frozenset()
    failure_cause: str | None = None

    @property
    def failed(self) -> bool:
        """Return True if the layer failed."""
        return self.failure_cause is not None

    @property
    def has_data(self) -> bool:
        """Return True if the layer has at least one included interface."""
        return self.included_count > 0


@dataclass(frozen=True, slots=True)
class LayerOutcome:
    """A layer result with the rows to export, which exist only for a layer with data."""

    result: LayerResult
    data: LayerData | None = None


@dataclass(frozen=True, slots=True)
class ExportSummary:
    """What was written in the report file [RF-042]."""

    path: Path
    sheet_count: int
    interface_count: int


@dataclass(frozen=True, slots=True)
class RunResult:
    """Overall result of the run once the layers were processed and the file written [RF-044].

    `export_summary` is None when no file was written, and `export_failed` tells whether that
    was because writing it failed. A run without any sheet writes no file and is failed.
    """

    layer_results: tuple[LayerResult, ...]
    missing_days: tuple[str, ...] = ()
    export_summary: ExportSummary | None = None
    export_failed: bool = field(default=False)

    @property
    def failed_layers(self) -> tuple[str, ...]:
        """Return the names of the failed layers."""
        return tuple(result.layer for result in self.layer_results if result.failed)

    @property
    def failed(self) -> bool:
        """Return True unless every layer succeeded, one had data and the file was written."""
        return (
            bool(self.failed_layers)
            or self.export_failed
            or self.export_summary is None
        )

    @property
    def exit_code(self) -> ExitCode:
        """Return 0 for a successful run and 1 for a failed one."""
        return ExitCode.FAILED if self.failed else ExitCode.SUCCESS
