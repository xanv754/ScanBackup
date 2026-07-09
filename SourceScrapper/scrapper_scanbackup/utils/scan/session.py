import requests
from scrapper_scanbackup.utils.config.load import ScrapperSetting


class ScanSession:
    _instance: "ScanSession | None" = None
    _current_session: requests.Session

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_initialized"):
            self._setting = ScrapperSetting()
            self._current_session = requests.Session()
            self._initialized = True

    def _log_in(self) -> None:
        credentials = self._setting.get_scan_credentials()
        self._current_session.post("", json={})
