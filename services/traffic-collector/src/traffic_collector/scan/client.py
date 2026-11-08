import threading
from typing import Protocol

import requests
import urllib3

from traffic_collector.constants.constants import (
    HTTP_ERROR_STATUS_THRESHOLD,
    HTTP_UNAUTHORIZED_STATUS,
)
from traffic_collector.scan.errors import (
    ScanEmptyResponse,
    ScanHttpError,
    ScanTimeout,
    ScanUnauthorized,
    ScanUnreachable,
)
from traffic_collector.settings import ScanCredentials

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ScanClient(Protocol):
    """Downloads the traffic log of an interface from SCAN."""

    def fetch(self, scan_url: str) -> str:
        """Return the body of `scan_url` or raise the `ScanError` that matches the failure."""
        ...


class HttpScanClient:
    """HTTP implementation of `ScanClient` with basic authentication and no retries.

    It is called from worker threads, so each thread gets its own `requests.Session`.
    TLS verification is disabled because SCAN uses a self-signed certificate.
    """

    def __init__(self, credentials: ScanCredentials, timeout_seconds: float) -> None:
        """Keep the credentials and the request timeout."""
        self._credentials = credentials
        self._timeout_seconds = timeout_seconds
        self._thread_sessions = threading.local()
        self._sessions: list[requests.Session] = []
        self._sessions_lock = threading.Lock()

    def fetch(self, scan_url: str) -> str:
        """Download the log [RF-016].

        Failures map to: `ScanTimeout`, `ScanUnreachable`, `ScanUnauthorized` (HTTP 401),
        `ScanHttpError` (any other HTTP >= 400) and `ScanEmptyResponse` [RF-022].
        """
        try:
            response = self._session().get(scan_url, timeout=self._timeout_seconds)
        except requests.Timeout as error:
            raise ScanTimeout() from error
        except requests.ConnectionError as error:
            raise ScanUnreachable() from error
        if response.status_code == HTTP_UNAUTHORIZED_STATUS:
            raise ScanUnauthorized()
        if response.status_code >= HTTP_ERROR_STATUS_THRESHOLD:
            raise ScanHttpError(response.status_code)
        if not response.text.strip():
            raise ScanEmptyResponse()
        return response.text

    def close(self) -> None:
        """Close the sessions of all the threads."""
        with self._sessions_lock:
            for session in self._sessions:
                session.close()
            self._sessions.clear()

    def _session(self) -> requests.Session:
        """Return the session of the current thread, creating it on first use."""
        session = getattr(self._thread_sessions, "session", None)
        if session is None:
            session = requests.Session()
            session.auth = (self._credentials.username, self._credentials.password)
            session.verify = False
            self._thread_sessions.session = session
            with self._sessions_lock:
                self._sessions.append(session)
        return session
