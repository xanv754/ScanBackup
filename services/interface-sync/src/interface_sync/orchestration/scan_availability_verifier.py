from interface_sync.constants.enums import LogEvent
from interface_sync.exceptions import ScanUnavailableError
from interface_sync.models import PageConfig
from interface_sync.scraping import ScanAvailabilityChecker
from interface_sync.utils.logger import ServiceLogger
from interface_sync.utils.terminal import Terminal


class ScanAvailabilityVerifier:
    """Checks the SCAN base URLs of the configuration and reports the result on the terminal.

    The log entries of each base URL are written by the checker; this class adds the terminal
    output and the general result. It is shared by the full run and the `check-scan` command.
    """

    def __init__(
        self, checker: ScanAvailabilityChecker, logger: ServiceLogger, terminal: Terminal
    ) -> None:
        """Receive the checker and the channels where the result is reported."""
        self._checker = checker
        self._logger = logger
        self._terminal = terminal

    def verify(self, pages: list[PageConfig]) -> None:
        """Check each SCAN base URL; raise `ScanUnavailableError` if any does not answer."""
        with self._terminal.loading("Verificando SCAN..."):
            checks = self._checker.check(pages)
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
        self._logger.info(LogEvent.SCAN_AVAILABLE, f"{len(checks)} rutas base")
        self._terminal.info(LogEvent.SCAN_AVAILABLE)
