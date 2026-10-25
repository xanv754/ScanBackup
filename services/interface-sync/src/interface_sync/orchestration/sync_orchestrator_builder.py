import os
from pathlib import Path

from interface_sync.constants.constants import (
    CONFIG_PATH_VARIABLE,
    DEFAULT_CONFIG_PATH,
    LOG_FILE_PATH,
)
from interface_sync.models import ScanCredentials
from interface_sync.orchestration.page_processor import PageProcessor
from interface_sync.orchestration.scan_availability_verifier import ScanAvailabilityVerifier
from interface_sync.orchestration.scan_check_orchestrator import ScanCheckOrchestrator
from interface_sync.orchestration.sync_orchestrator import SyncOrchestrator
from interface_sync.persistence import InterfaceRepository, MongoConnection, MongoSettings
from interface_sync.scraping import (
    PageParserFactory,
    PageScraper,
    ScanAvailabilityChecker,
    ScanClient,
)
from interface_sync.synchronization import (
    ChangeReporter,
    InterfaceChangePlanner,
    LayerDecommissioner,
    ScanUrlClaims,
)
from interface_sync.utils.configuration import ConfigurationFile
from interface_sync.utils.logger import ServiceLogger
from interface_sync.utils.terminal import Terminal
from interface_sync.validation import CapacityValidator, CompletenessValidator, ListingValidator


class SyncOrchestratorBuilder:
    """Composition root: creates every dependency of the run and injects it.

    It owns the `ScanClient` and the `MongoConnection`, so `close` must be called when the run
    ends. The configuration path comes from `CONFIG_PATH`.
    """

    def __init__(self) -> None:
        """Create the logger and the terminal shared by the whole run."""
        self._logger = ServiceLogger(LOG_FILE_PATH)
        self._terminal = Terminal()
        self._client: ScanClient | None = None
        self._connection: MongoConnection | None = None

    @property
    def logger(self) -> ServiceLogger:
        """Return the logger of the run."""
        return self._logger

    @property
    def terminal(self) -> Terminal:
        """Return the terminal of the run."""
        return self._terminal

    def build_scan_check(self) -> ScanCheckOrchestrator:
        """Return the orchestrator that only checks SCAN; it needs no database settings.

        Raise `MissingCredentialsError` when the SCAN credentials are not in the environment.
        """
        self._client = ScanClient(ScanCredentials.from_environment())
        return ScanCheckOrchestrator(
            ConfigurationFile(self._config_path(), self._logger),
            self._build_scan_availability_verifier(self._client),
            self._logger,
            self._terminal,
        )

    def build(self) -> SyncOrchestrator:
        """Return the orchestrator.

        Raise `MissingCredentialsError` or `MissingDatabaseSettingsError` when the SCAN
        credentials or the database settings are not in the environment.
        """
        scan_credentials = ScanCredentials.from_environment()
        mongo_settings = MongoSettings.from_environment()
        self._client = ScanClient(scan_credentials)
        self._connection = MongoConnection(mongo_settings)
        repository = InterfaceRepository(self._connection.database)
        planner = InterfaceChangePlanner()
        change_reporter = ChangeReporter(self._logger)
        listing_validator = ListingValidator(
            CompletenessValidator(), CapacityValidator(), self._logger
        )
        page_processor = PageProcessor(
            PageScraper(self._client, PageParserFactory(self._client)),
            listing_validator,
            repository,
            planner,
            change_reporter,
            ScanUrlClaims(),
            self._logger,
        )
        return SyncOrchestrator(
            ConfigurationFile(self._config_path(), self._logger),
            self._build_scan_availability_verifier(self._client),
            page_processor,
            LayerDecommissioner(repository, planner, change_reporter, self._logger),
            repository,
            self._logger,
            self._terminal,
        )

    def _config_path(self) -> Path:
        """Return the path of `config.yml` taken from `CONFIG_PATH` or the default one."""
        return Path(os.environ.get(CONFIG_PATH_VARIABLE, DEFAULT_CONFIG_PATH))

    def _build_scan_availability_verifier(self, client: ScanClient) -> ScanAvailabilityVerifier:
        """Return the SCAN availability verifier that probes through `client`."""
        return ScanAvailabilityVerifier(
            ScanAvailabilityChecker(client, self._logger), self._logger, self._terminal
        )

    def close(self) -> None:
        """Release the resources created by `build`."""
        if self._client is not None:
            self._client.close()
        if self._connection is not None:
            self._connection.close()
