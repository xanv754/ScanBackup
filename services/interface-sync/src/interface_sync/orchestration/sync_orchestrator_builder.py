import os
from pathlib import Path

from interface_sync.constants.constants import (
    CONFIG_PATH_VARIABLE,
    DEFAULT_CONFIG_PATH,
    LOG_FILE_PATH,
)
from interface_sync.models import ScanCredentials
from interface_sync.orchestration.page_processor import PageProcessor
from interface_sync.orchestration.sync_orchestrator import SyncOrchestrator
from interface_sync.scraping import PageParserFactory, PageScraper, ScanClient
from interface_sync.utils.configuration import ConfigurationFile
from interface_sync.utils.logger import ServiceLogger
from interface_sync.utils.terminal import Terminal
from interface_sync.validation import CapacityValidator, CompletenessValidator, ListingValidator


class SyncOrchestratorBuilder:
    """Composition root: creates every dependency of the run and injects it.

    It owns the `ScanClient`, so `close` must be called when the run ends. The
    configuration path comes from `CONFIG_PATH`.
    """

    def __init__(self) -> None:
        """Create the logger and the terminal shared by the whole run."""
        self._logger = ServiceLogger(LOG_FILE_PATH)
        self._terminal = Terminal()
        self._client: ScanClient | None = None

    @property
    def logger(self) -> ServiceLogger:
        """Return the logger of the run."""
        return self._logger

    @property
    def terminal(self) -> Terminal:
        """Return the terminal of the run."""
        return self._terminal

    def build(self) -> SyncOrchestrator:
        """Return the orchestrator; raise `MissingCredentialsError` without SCAN credentials."""
        self._client = ScanClient(ScanCredentials.from_environment())
        config_path = Path(os.environ.get(CONFIG_PATH_VARIABLE, DEFAULT_CONFIG_PATH))
        listing_validator = ListingValidator(
            CompletenessValidator(), CapacityValidator(), self._logger
        )
        page_processor = PageProcessor(
            PageScraper(self._client, PageParserFactory(self._client)),
            listing_validator,
            self._logger,
        )
        return SyncOrchestrator(
            ConfigurationFile(config_path, self._logger),
            page_processor,
            self._logger,
            self._terminal,
        )

    def close(self) -> None:
        """Release the resources created by `build`."""
        if self._client is not None:
            self._client.close()
