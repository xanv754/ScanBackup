from interface_sync.constants.enums import LogEvent
from interface_sync.exceptions import PageFetchError
from interface_sync.models import BaseUrlCheck, PageConfig
from interface_sync.scraping.scan_prober import ScanProber
from interface_sync.utils.logger import ServiceLogger


class ScanAvailabilityChecker:
    """Checks that every distinct SCAN base URL declared in `config.yml` answers.

    Pages sharing a base URL (scheme and host) are checked once. Every base URL is checked
    and logged, so the operator sees all the failures of a run and not only the first.
    """

    def __init__(self, prober: ScanProber, logger: ServiceLogger) -> None:
        """Receive the prober that talks to SCAN and the logger of the run."""
        self._prober = prober
        self._logger = logger

    def check(self, pages: list[PageConfig]) -> list[BaseUrlCheck]:
        """Return one check per distinct base URL, in the order of the configuration."""
        base_urls = dict.fromkeys(page.base_url for page in pages)
        return [self._check_base_url(base_url) for base_url in base_urls]

    def _check_base_url(self, base_url: str) -> BaseUrlCheck:
        """Probe one base URL and log the outcome."""
        try:
            self._prober.probe(base_url)
        except PageFetchError as error:
            self._logger.error(LogEvent.SCAN_BASE_UNREACHABLE, f"{base_url} ({error.cause})")
            return BaseUrlCheck(base_url=base_url, cause=error.cause)
        self._logger.info(LogEvent.SCAN_BASE_RESPONDED, base_url)
        return BaseUrlCheck(base_url=base_url)
