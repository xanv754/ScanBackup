from interface_sync.constants.enums import LogEvent
from interface_sync.exceptions import InvalidConfigError, ServiceStartupError
from interface_sync.models import ExitCode
from interface_sync.orchestration.scan_availability_verifier import ScanAvailabilityVerifier
from interface_sync.utils.configuration import ConfigurationFile
from interface_sync.utils.logger import ServiceLogger
from interface_sync.utils.terminal import Terminal


class ScanCheckOrchestrator:
    """Runs only the SCAN availability check and returns the exit code of the process.

    It loads the configuration and checks its base URLs; it never touches the database.
    Returns `SUCCESS` when every base URL answers and `PROCESS_ERROR` otherwise.
    """

    def __init__(
        self,
        configuration_file: ConfigurationFile,
        scan_availability_verifier: ScanAvailabilityVerifier,
        logger: ServiceLogger,
        terminal: Terminal,
    ) -> None:
        """Receive the collaborators of the check."""
        self._configuration_file = configuration_file
        self._scan_availability_verifier = scan_availability_verifier
        self._logger = logger
        self._terminal = terminal

    def run(self) -> ExitCode:
        """Execute the check and return `SUCCESS` or `PROCESS_ERROR`."""
        try:
            pages = self._configuration_file.load()
            self._terminal.info(f"{LogEvent.CONFIG_LOADED}: {len(pages)} páginas")
            self._scan_availability_verifier.verify(pages)
        except InvalidConfigError as error:
            for cause in error.causes:
                self._terminal.error(f"{LogEvent.INVALID_CONFIG}: {cause}")
            return self._fail_process(LogEvent.INVALID_CONFIG)
        except ServiceStartupError as error:
            self._terminal.error(str(error))
            return self._fail_process(str(error))
        return ExitCode.SUCCESS

    def _fail_process(self, cause: str) -> ExitCode:
        """Log a general process error and return its exit code."""
        self._logger.error(LogEvent.PROCESS_ERROR, cause)
        return ExitCode.PROCESS_ERROR
