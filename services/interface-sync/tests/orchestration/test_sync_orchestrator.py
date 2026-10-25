from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import pytest

from interface_sync.constants.enums import LogEvent
from interface_sync.exceptions import DatabaseUnavailableError, InvalidConfigError
from interface_sync.models import BaseUrlCheck, ExitCode, LayerResult, PageConfig, PageResult
from interface_sync.orchestration import SyncOrchestrator
from interface_sync.utils.terminal import Terminal


class RecordingTerminal(Terminal):
    def __init__(self) -> None:
        self.lines: list[tuple[str, str]] = []

    def info(self, message: str) -> None:
        self.lines.append(("info", message))

    def warning(self, message: str) -> None:
        self.lines.append(("warning", message))

    def error(self, message: str) -> None:
        self.lines.append(("error", message))

    @contextmanager
    def loading(self, message: str) -> Iterator[None]:
        yield

    def messages(self, level: str) -> list[str]:
        return [message for line_level, message in self.lines if line_level == level]


class FakeConfigurationFile:
    def __init__(self, pages: list[PageConfig] | InvalidConfigError) -> None:
        self._pages = pages

    def load(self) -> list[PageConfig]:
        if isinstance(self._pages, InvalidConfigError):
            raise self._pages
        return self._pages


class FakeScanAvailabilityChecker:
    def __init__(self, unreachable: dict[str, str] | None = None) -> None:
        self._unreachable = unreachable or {}
        self.checked = False

    def check(self, pages: list[PageConfig]) -> list[BaseUrlCheck]:
        self.checked = True
        return [
            BaseUrlCheck(base_url=page.base_url, cause=self._unreachable.get(page.base_url))
            for page in pages
        ]


class FakePageProcessor:
    def __init__(self, results: dict[str, PageResult]) -> None:
        self._results = results
        self.processed: list[str] = []

    def process(self, page: PageConfig) -> PageResult:
        self.processed.append(page.label)
        return self._results[page.label]


class FakeLayerDecommissioner:
    def __init__(self, layer_results: list[LayerResult] | None = None) -> None:
        self._layer_results = layer_results or []
        self.received: list[PageResult] | None = None

    def decommission(self, page_results: list[PageResult]) -> list[LayerResult]:
        self.received = page_results
        return self._layer_results


class FakeRepository:
    def __init__(self, error: DatabaseUnavailableError | None = None) -> None:
        self._error = error
        self.prepared = False

    def prepare(self) -> None:
        if self._error:
            raise self._error
        self.prepared = True


BORDE_PAGE = PageConfig(layer="borde", url="http://scan/borde", vendor="huawei")
DIST_PAGE = PageConfig(layer="dist", url="http://scan/dist", vendor="huawei")


def build_orchestrator(
    pages: list[PageConfig] | InvalidConfigError,
    results: dict[str, PageResult],
    layer_results: list[LayerResult],
    recording_logger: Any,
    repository: FakeRepository | None = None,
    checker: FakeScanAvailabilityChecker | None = None,
) -> tuple[SyncOrchestrator, RecordingTerminal, FakePageProcessor, FakeLayerDecommissioner]:
    terminal = RecordingTerminal()
    processor = FakePageProcessor(results)
    decommissioner = FakeLayerDecommissioner(layer_results)
    orchestrator = SyncOrchestrator(
        FakeConfigurationFile(pages),  # type: ignore[arg-type]
        checker or FakeScanAvailabilityChecker(),  # type: ignore[arg-type]
        processor,  # type: ignore[arg-type]
        decommissioner,  # type: ignore[arg-type]
        repository or FakeRepository(),  # type: ignore[arg-type]
        recording_logger,
        terminal,
    )
    return orchestrator, terminal, processor, decommissioner


def ok(page: PageConfig) -> PageResult:
    return PageResult(page_label=page.label, layer=page.layer, present_scan_urls=frozenset({"u"}))


def test_everything_succeeding_exits_with_zero(recording_logger: Any):
    """RF-013: exit code 0 only when every page and every layer succeeded."""
    orchestrator, terminal, _, decommissioner = build_orchestrator(
        [BORDE_PAGE, DIST_PAGE],
        {BORDE_PAGE.label: ok(BORDE_PAGE), DIST_PAGE.label: ok(DIST_PAGE)},
        [LayerResult(layer="BORDE", decommissioned_count=2), LayerResult(layer="DIST")],
        recording_logger,
    )

    assert orchestrator.run() is ExitCode.SUCCESS
    assert terminal.messages("error") == []
    assert ("info", f"{LogEvent.GENERAL_SUCCEEDED}: 2 páginas") in terminal.lines
    assert decommissioner.received is not None
    assert len(decommissioner.received) == 2


def test_database_is_prepared_before_any_page(recording_logger: Any):
    """The indexes and connection are checked at startup."""
    repository = FakeRepository()
    orchestrator, _, _, _ = build_orchestrator(
        [BORDE_PAGE], {BORDE_PAGE.label: ok(BORDE_PAGE)}, [], recording_logger, repository
    )

    orchestrator.run()

    assert repository.prepared


def test_database_unavailable_at_startup_is_a_process_error_without_pages(
    recording_logger: Any,
):
    """RF-013: with the database down no page is processed and the exit code is 2."""
    repository = FakeRepository(DatabaseUnavailableError("Base de datos no disponible (X)"))
    orchestrator, terminal, processor, decommissioner = build_orchestrator(
        [BORDE_PAGE], {BORDE_PAGE.label: ok(BORDE_PAGE)}, [], recording_logger, repository
    )

    assert orchestrator.run() is ExitCode.PROCESS_ERROR
    assert processor.processed == []
    assert decommissioner.received is None
    assert terminal.messages("error") == ["Base de datos no disponible (X)"]
    assert recording_logger.messages("error") == [LogEvent.PROCESS_ERROR]


def test_invalid_configuration_is_a_process_error_without_pages(recording_logger: Any):
    """RF-002: an invalid config.yml stops the run before any page or database access."""
    repository = FakeRepository()
    orchestrator, _, processor, _ = build_orchestrator(
        InvalidConfigError(["causa"]), {}, [], recording_logger, repository
    )

    assert orchestrator.run() is ExitCode.PROCESS_ERROR
    assert processor.processed == []
    assert not repository.prepared


def test_scraping_failure_fails_the_run_but_keeps_processing(recording_logger: Any):
    """RF-010: a failed page does not stop the rest, and the run exits with 1."""
    failed = PageResult(page_label=BORDE_PAGE.label, layer="BORDE", cause="sin conexión a SCAN")
    orchestrator, terminal, processor, decommissioner = build_orchestrator(
        [BORDE_PAGE, DIST_PAGE],
        {BORDE_PAGE.label: failed, DIST_PAGE.label: ok(DIST_PAGE)},
        [LayerResult(layer="BORDE", skipped_reason="páginas fallidas: BORDE HUAWEI")],
        recording_logger,
    )

    assert orchestrator.run() is ExitCode.FAILED
    assert processor.processed == [BORDE_PAGE.label, DIST_PAGE.label]
    assert decommissioner.received is not None
    assert any(LogEvent.PAGE_FAILED in message for message in terminal.messages("error"))
    assert any(LogEvent.LAYER_SKIPPED in message for message in terminal.messages("warning"))


def test_database_failure_is_named_apart_and_fails_the_run(recording_logger: Any):
    """Scraping and database results are separate: scraping succeeds, the database fails, exit 1."""
    failed = PageResult(
        page_label=BORDE_PAGE.label, layer="BORDE", database_cause="error de base de datos"
    )
    orchestrator, terminal, _, _ = build_orchestrator(
        [BORDE_PAGE], {BORDE_PAGE.label: failed}, [], recording_logger
    )

    assert orchestrator.run() is ExitCode.FAILED
    assert ("info", f"{LogEvent.SCRAPING_SUCCEEDED}: {BORDE_PAGE.label}") in terminal.lines
    assert (
        "error",
        f"{LogEvent.DATABASE_FAILED}: {BORDE_PAGE.label} (error de base de datos)",
    ) in terminal.lines
    assert recording_logger.messages("error") == [LogEvent.GENERAL_FAILED]


def test_layer_database_failure_fails_the_run_even_if_every_page_succeeded(
    recording_logger: Any,
):
    """RF-010: a database error while decommissioning a layer makes the process exit with 1."""
    orchestrator, terminal, _, _ = build_orchestrator(
        [BORDE_PAGE],
        {BORDE_PAGE.label: ok(BORDE_PAGE)},
        [LayerResult(layer="BORDE", database_cause="error de base de datos")],
        recording_logger,
    )

    assert orchestrator.run() is ExitCode.FAILED
    assert (
        "error",
        f"{LogEvent.DATABASE_FAILED}: BORDE (error de base de datos)",
    ) in terminal.lines
    assert "BORDE (desincorporación)" in recording_logger.records[-1][2]


def test_layer_summary_is_printed_per_layer(recording_logger: Any):
    """The decommission result is shown by layer."""
    orchestrator, terminal, _, _ = build_orchestrator(
        [BORDE_PAGE, DIST_PAGE],
        {BORDE_PAGE.label: ok(BORDE_PAGE), DIST_PAGE.label: ok(DIST_PAGE)},
        [LayerResult(layer="BORDE", decommissioned_count=3), LayerResult(layer="DIST")],
        recording_logger,
    )

    orchestrator.run()

    assert ("info", f"{LogEvent.LAYER_SUMMARY}: BORDE (desincorporadas: 3)") in terminal.lines
    assert ("info", f"{LogEvent.LAYER_SUMMARY}: DIST (desincorporadas: 0)") in terminal.lines


@pytest.mark.parametrize("pages", [[BORDE_PAGE], [BORDE_PAGE, DIST_PAGE]])
def test_decommission_runs_once_after_all_pages(recording_logger: Any, pages: list[PageConfig]):
    """RF-009: the layer decommission needs every page, so it runs once at the end."""
    results = {page.label: ok(page) for page in pages}
    orchestrator, _, processor, decommissioner = build_orchestrator(
        pages, results, [], recording_logger
    )

    orchestrator.run()

    assert processor.processed == [page.label for page in pages]
    assert decommissioner.received == [results[page.label] for page in pages]


def test_scan_unavailable_is_a_process_error_without_pages_or_database(recording_logger: Any):
    """Startup: a SCAN base URL without answer stops the run before the database and pages."""
    repository = FakeRepository()
    checker = FakeScanAvailabilityChecker({"http://scan": "sin conexión a SCAN"})
    orchestrator, terminal, processor, _ = build_orchestrator(
        [BORDE_PAGE, DIST_PAGE], {}, [], recording_logger, repository, checker
    )

    assert orchestrator.run() is ExitCode.PROCESS_ERROR
    assert processor.processed == []
    assert not repository.prepared
    assert (
        "error",
        f"{LogEvent.SCAN_BASE_UNREACHABLE}: http://scan (sin conexión a SCAN)",
    ) in terminal.lines
    assert terminal.messages("error")[-1].startswith("SCAN no disponible")
    assert recording_logger.messages("error") == [LogEvent.PROCESS_ERROR]


def test_scan_available_is_reported_per_base_url(recording_logger: Any):
    """Startup: each answering base URL is printed and the run continues."""
    checker = FakeScanAvailabilityChecker()
    orchestrator, terminal, processor, _ = build_orchestrator(
        [BORDE_PAGE], {BORDE_PAGE.label: ok(BORDE_PAGE)}, [], recording_logger, checker=checker
    )

    orchestrator.run()

    assert checker.checked
    assert ("info", f"{LogEvent.SCAN_BASE_RESPONDED}: http://scan") in terminal.lines
    assert ("info", LogEvent.SCAN_AVAILABLE) in terminal.lines
    assert processor.processed == [BORDE_PAGE.label]
