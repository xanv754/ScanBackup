from datetime import date, timedelta
from scanbackup.infrastructure import (
    MongoTrafficHistoryBBIPRepository,
    MongoTrafficSourceBBIPRepository,
    MongoIPHistoryBBIPRepository,
    MongoIPSourceBBIPRepository,
    MRTGFetcher,
    IPActiveFetcher,
)
from scanbackup.application.use_case.bbip.updaters.traffic_collector import (
    TrafficCollectorUseCase,
)
from scanbackup.application.use_case.bbip.updaters.ip_collector import (
    IPCollectorUseCase,
)
from scanbackup.shared import Configuration


class TrafficHistoryUpdater:
    @staticmethod
    def execute(date_str: str | None = None) -> None:
        """Collect the SCAN traffic of every active source and store it in the system.

        Args:
            date_str (str | None): The day to collect, formatted as YYYY-MM-DD.
                Defaults to yesterday when omitted.
        """
        if not date_str:
            yesterday = date.today() - timedelta(days=1)
            date_str = yesterday.strftime("%Y-%m-%d")

        scanner_config = Configuration().get_cfg_metadata().scanner
        fetcher = MRTGFetcher(
            username=scanner_config.scan_credentials.username.strip(),
            password=scanner_config.scan_credentials.password.strip(),
        )

        use_case = TrafficCollectorUseCase(
            source_repository=MongoTrafficSourceBBIPRepository(),
            history_repository_factory=MongoTrafficHistoryBBIPRepository,
            fetcher=fetcher,
            data_date=date_str,
            max_workers=scanner_config.max_workers,
        )

        use_case.execute()


class IPHistoryUpdater:
    @staticmethod
    def execute(date_str: str | None = None) -> None:
        """Collect the SCAN active-IP count of every active source and store it in the system.

        Args:
            date_str (str | None): The day to collect, formatted as YYYY-MM-DD.
                Defaults to yesterday when omitted.
        """
        if not date_str:
            yesterday = date.today() - timedelta(days=1)
            date_str = yesterday.strftime("%Y-%m-%d")

        scanner_config = Configuration().get_cfg_metadata().scanner
        fetcher = IPActiveFetcher(
            username=scanner_config.scan_credentials.username.strip(),
            password=scanner_config.scan_credentials.password.strip(),
        )

        use_case = IPCollectorUseCase(
            source_repository=MongoIPSourceBBIPRepository(),
            history_repository_factory=MongoIPHistoryBBIPRepository,
            fetcher=fetcher,
            data_date=date_str,
            max_workers=scanner_config.max_workers,
        )

        use_case.execute()
