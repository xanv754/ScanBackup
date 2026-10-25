from interface_sync.exceptions import InvalidConfigError, ServiceStartupError
from interface_sync.models import ExitCode, PageConfig, PageResult
from interface_sync.orchestration.page_processor import PageProcessor
from interface_sync.utils.configuration import ConfigurationFile
from interface_sync.utils.logger import ServiceLogger
from interface_sync.utils.terminal import Terminal


class SyncOrchestrator:
    """Coordinates the whole synchronization run and returns the exit code of the process.

    Order: load the configuration, check SCAN, check the database and process each page.
    Any failure before the pages is a process error and no page is processed. Once the
    pages start, one failed page never stops the rest [RF-010, RF-012, RF-013].
    """

    def __init__(
        self,
        configuration_file: ConfigurationFile,
        page_processor: PageProcessor,
        logger: ServiceLogger,
        terminal: Terminal,
    ) -> None:
        """Receive the collaborators of the run."""
        self._configuration_file = configuration_file
        self._page_processor = page_processor
        self._logger = logger
        self._terminal = terminal

    def run(self) -> ExitCode:
        """Execute the synchronization and return `SUCCESS`, `FAILED` or `PROCESS_ERROR`."""
        try:
            pages = self._configuration_file.load()
            self._terminal.info(f"Configuración cargada: {len(pages)} páginas")
            self._verify_scan_available()
            self._verify_database_available()
        except InvalidConfigError as error:
            for cause in error.causes:
                self._terminal.error(f"Configuración inválida: {cause}")
            return self._fail_process("Configuración inválida")
        except ServiceStartupError as error:
            self._terminal.error(str(error))
            return self._fail_process(str(error))

        results = [self._process_page(page) for page in pages]
        return self._report_results(results)

    def _verify_scan_available(self) -> None:
        """Check that SCAN answers; raise `ServiceStartupError` when it does not."""
        # TODO: implement the SCAN availability check and report it with the terminal.
        self._terminal.info("Verificación de SCAN pendiente de implementar")

    def _verify_database_available(self) -> None:
        """Check that the database answers; raise `ServiceStartupError` when it does not."""
        # TODO: implement the database availability check and report it with the terminal.
        self._terminal.info("Verificación de la base de datos pendiente de implementar")

    def _process_page(self, page: PageConfig) -> PageResult:
        """Process one page showing a spinner and print its result."""
        with self._terminal.loading(f"Obteniendo interfaces de {page.label}..."):
            result = self._page_processor.process(page)
        if result.succeeded:
            self._terminal.info(f"Página exitosa: {result.page_label}")
        else:
            self._terminal.error(f"Página fallida: {result.page_label} ({result.cause})")
        return result

    def _report_results(self, results: list[PageResult]) -> ExitCode:
        """Log and print the general result and return the matching exit code."""
        failed_labels = [result.page_label for result in results if not result.succeeded]
        if failed_labels:
            summary = f"{len(failed_labels)} de {len(results)} páginas fallidas"
            self._logger.error(
                "Resultado general fallido", f"{summary}: {', '.join(failed_labels)}"
            )
            self._terminal.error(f"Resultado general fallido: {summary}")
            return ExitCode.FAILED
        self._logger.info("Resultado general exitoso", f"{len(results)} páginas")
        self._terminal.info(f"Resultado general exitoso: {len(results)} páginas")
        return ExitCode.SUCCESS

    def _fail_process(self, cause: str) -> ExitCode:
        """Log a general process error and return its exit code."""
        self._logger.error("Error general del proceso", cause)
        return ExitCode.PROCESS_ERROR
