from interface_sync.constants.enums import LogEvent
from interface_sync.exceptions import (
    InvalidConfigError,
    ScanUnavailableError,
    ServiceStartupError,
)
from interface_sync.models import ExitCode, LayerResult, PageConfig, PageResult
from interface_sync.orchestration.page_processor import PageProcessor
from interface_sync.persistence import InterfaceRepository
from interface_sync.scraping import ScanAvailabilityChecker
from interface_sync.synchronization import LayerDecommissioner
from interface_sync.utils.configuration import ConfigurationFile
from interface_sync.utils.logger import ServiceLogger
from interface_sync.utils.terminal import Terminal


class SyncOrchestrator:
    """Coordinates the whole synchronization run and returns the exit code of the process.

    Order: load the configuration, check every SCAN base URL, check the database, process each
    page and decommission the missing interfaces of each layer. Any failure before the pages is a
    process error and no page is processed. Once the pages start, one failed page never stops
    the rest. Scraping and database results are reported apart, but either one failing makes
    the general result fail [RF-010, RF-012, RF-013].
    """

    def __init__(
        self,
        configuration_file: ConfigurationFile,
        scan_availability_checker: ScanAvailabilityChecker,
        page_processor: PageProcessor,
        layer_decommissioner: LayerDecommissioner,
        repository: InterfaceRepository,
        logger: ServiceLogger,
        terminal: Terminal,
    ) -> None:
        """Receive the collaborators of the run."""
        self._configuration_file = configuration_file
        self._scan_availability_checker = scan_availability_checker
        self._page_processor = page_processor
        self._layer_decommissioner = layer_decommissioner
        self._repository = repository
        self._logger = logger
        self._terminal = terminal

    def run(self) -> ExitCode:
        """Execute the synchronization and return `SUCCESS`, `FAILED` or `PROCESS_ERROR`."""
        try:
            pages = self._configuration_file.load()
            self._terminal.info(f"{LogEvent.CONFIG_LOADED}: {len(pages)} páginas")
            self._verify_scan_available(pages)
            self._verify_database_available()
        except InvalidConfigError as error:
            for cause in error.causes:
                self._terminal.error(f"{LogEvent.INVALID_CONFIG}: {cause}")
            return self._fail_process(LogEvent.INVALID_CONFIG)
        except ServiceStartupError as error:
            self._terminal.error(str(error))
            return self._fail_process(str(error))

        page_results = [self._process_page(page) for page in pages]
        layer_results = self._decommission_layers(page_results)
        return self._report_results(page_results, layer_results)

    def _verify_scan_available(self, pages: list[PageConfig]) -> None:
        """Check each SCAN base URL; raise `ScanUnavailableError` if any does not answer."""
        with self._terminal.loading("Verificando SCAN..."):
            checks = self._scan_availability_checker.check(pages)
        for check in checks:
            if check.responded:
                self._terminal.info(f"{LogEvent.SCAN_BASE_RESPONDED}: {check.base_url}")
            else:
                self._terminal.error(
                    f"{LogEvent.SCAN_BASE_UNREACHABLE}: {check.base_url} ({check.cause})"
                )
        unreachable_count = sum(1 for check in checks if not check.responded)
        if unreachable_count:
            raise ScanUnavailableError(
                f"SCAN no disponible: {unreachable_count} de {len(checks)} rutas base sin respuesta"
            )
        self._terminal.info(LogEvent.SCAN_AVAILABLE)

    def _verify_database_available(self) -> None:
        """Check that the database answers and prepare its indexes; raise `ServiceStartupError`."""
        self._repository.prepare()
        self._terminal.info(LogEvent.DATABASE_READY)

    def _process_page(self, page: PageConfig) -> PageResult:
        """Process one page showing a spinner and print its scraping and database results."""
        with self._terminal.loading(f"Procesando {page.label}..."):
            result = self._page_processor.process(page)
        if not result.scraping_succeeded:
            self._terminal.error(f"{LogEvent.PAGE_FAILED}: {result.page_label} ({result.cause})")
        elif not result.database_succeeded:
            self._terminal.info(f"{LogEvent.SCRAPING_SUCCEEDED}: {result.page_label}")
            self._terminal.error(
                f"{LogEvent.DATABASE_FAILED}: {result.page_label} ({result.database_cause})"
            )
        else:
            self._terminal.info(f"{LogEvent.PAGE_SUCCEEDED}: {result.page_label}")
        return result

    def _decommission_layers(self, page_results: list[PageResult]) -> list[LayerResult]:
        """Decommission the missing interfaces of each layer and print the result per layer."""
        with self._terminal.loading("Desincorporando interfaces ausentes..."):
            layer_results = self._layer_decommissioner.decommission(page_results)
        for layer_result in layer_results:
            if layer_result.skipped_reason:
                self._terminal.warning(
                    f"{LogEvent.LAYER_SKIPPED}: {layer_result.layer} "
                    f"({layer_result.skipped_reason})"
                )
            elif not layer_result.succeeded:
                self._terminal.error(
                    f"{LogEvent.DATABASE_FAILED}: {layer_result.layer} "
                    f"({layer_result.database_cause})"
                )
            else:
                self._terminal.info(
                    f"{LogEvent.LAYER_SUMMARY}: {layer_result.layer} "
                    f"(desincorporadas: {layer_result.decommissioned_count})"
                )
        return layer_results

    def _report_results(
        self, page_results: list[PageResult], layer_results: list[LayerResult]
    ) -> ExitCode:
        """Log and print the general result and return the matching exit code."""
        failed_labels = [result.page_label for result in page_results if not result.succeeded]
        failed_labels.extend(
            f"{result.layer} (desincorporación)" for result in layer_results if not result.succeeded
        )
        if failed_labels:
            summary = f"{len(failed_labels)} operaciones fallidas"
            self._logger.error(LogEvent.GENERAL_FAILED, f"{summary}: {', '.join(failed_labels)}")
            self._terminal.error(
                f"{LogEvent.GENERAL_FAILED}: {summary} ({', '.join(failed_labels)})"
            )
            return ExitCode.FAILED
        self._logger.info(LogEvent.GENERAL_SUCCEEDED, f"{len(page_results)} páginas")
        self._terminal.info(f"{LogEvent.GENERAL_SUCCEEDED}: {len(page_results)} páginas")
        return ExitCode.SUCCESS

    def _fail_process(self, cause: str) -> ExitCode:
        """Log a general process error and return its exit code."""
        self._logger.error(LogEvent.PROCESS_ERROR, cause)
        return ExitCode.PROCESS_ERROR
