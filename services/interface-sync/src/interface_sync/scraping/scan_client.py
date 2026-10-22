import requests
import urllib3

from interface_sync.exceptions import (
    ScanConnectionError,
    ScanHttpError,
    ScanTimeoutError,
    ScanUnauthorizedError,
)
from interface_sync.models import ScanCredentials

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ScanClient:
    """Downloads SCAN pages with basic authentication, reusing one HTTP session.

    TLS verification is always disabled because SCAN uses a self-signed certificate.
    """

    UNAUTHORIZED_STATUS = 401
    ERROR_STATUS_THRESHOLD = 400

    def __init__(
        self,
        credentials: ScanCredentials,
        session: requests.Session | None = None,
        timeout_seconds: float = 30,
    ) -> None:
        """Configure the session with the credentials and the request timeout."""
        self._session = session or requests.Session()
        self._session.auth = (credentials.username, credentials.password)
        self._session.verify = False
        self._timeout_seconds = timeout_seconds

    def fetch_html(self, url: str) -> str:
        """Return the body of the page, or raise the `PageFetchError` that matches the failure."""
        try:
            response = self._session.get(url, timeout=self._timeout_seconds)
        except requests.Timeout as error:
            raise ScanTimeoutError() from error
        except requests.ConnectionError as error:
            raise ScanConnectionError() from error
        if response.status_code == self.UNAUTHORIZED_STATUS:
            raise ScanUnauthorizedError()
        if response.status_code >= self.ERROR_STATUS_THRESHOLD:
            raise ScanHttpError(response.status_code)
        return response.text

    def close(self) -> None:
        """Release the underlying HTTP session."""
        self._session.close()

    def __enter__(self) -> "ScanClient":
        """Return the client itself for use in a `with` block."""
        return self

    def __exit__(self, *_exception_info: object) -> None:
        """Close the session when the `with` block ends."""
        self.close()
