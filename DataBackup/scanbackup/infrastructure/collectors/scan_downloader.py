import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SCANLogDownloader:
    """Downloads a raw SCAN log over HTTP, shared by every SCAN-based fetcher."""

    _TIMEOUT_SECONDS = 180
    _MAX_ATTEMPTS = 2

    def __init__(self, username: str, password: str) -> None:
        """Store the SCAN credentials used to authenticate every download."""
        self._auth = (username, password)

    def download(self, url: str) -> str:
        """Downloads the raw log body at `url`, retrying transient failures but not authentication errors."""
        last_error: Exception | None = None
        for _ in range(self._MAX_ATTEMPTS):
            try:
                response = requests.get(
                    url, auth=self._auth, timeout=self._TIMEOUT_SECONDS, verify=False
                )
                response.raise_for_status()
                return response.text
            except requests.HTTPError as error:
                if error.response is not None and error.response.status_code == 401:
                    raise
                last_error = error
            except requests.RequestException as error:
                last_error = error
        raise ConnectionError(f"Fallo al descargar {url}") from last_error
