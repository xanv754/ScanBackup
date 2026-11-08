import socket
import threading
from collections.abc import Iterator

import pytest

from tests.scan.conftest import LOG_BODY, PASSWORD, USERNAME
from traffic_collector.scan import (
    HttpScanClient,
    ScanEmptyResponse,
    ScanHttpError,
    ScanTimeout,
    ScanUnauthorized,
    ScanUnreachable,
)
from traffic_collector.settings import ScanCredentials

CREDENTIALS = ScanCredentials(username=USERNAME, password=PASSWORD)


@pytest.fixture
def client() -> Iterator[HttpScanClient]:
    http_client = HttpScanClient(CREDENTIALS, timeout_seconds=0.3)
    yield http_client
    http_client.close()


def test_fetch_returns_the_body(client: HttpScanClient, scan_simulator_url: str) -> None:
    """A successful answer returns the log text with basic auth (RF-016)."""
    assert client.fetch(f"{scan_simulator_url}/ok.log") == LOG_BODY


def test_slow_answer_is_a_timeout(client: HttpScanClient, scan_simulator_url: str) -> None:
    """An answer slower than the timeout is a timeout, not a connection error (RF-022)."""
    with pytest.raises(ScanTimeout):
        client.fetch(f"{scan_simulator_url}/hang.log")


def test_closed_port_is_unreachable(client: HttpScanClient) -> None:
    """A refused connection is "sin conexión a SCAN" (RF-022)."""
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]

    with pytest.raises(ScanUnreachable):
        client.fetch(f"http://127.0.0.1:{port}/ok.log")


def test_wrong_credentials_are_unauthorized(scan_simulator_url: str) -> None:
    """HTTP 401 is "credenciales rechazadas" (RF-022)."""
    wrong = HttpScanClient(ScanCredentials(username=USERNAME, password="wrong"), 1)

    with pytest.raises(ScanUnauthorized):
        wrong.fetch(f"{scan_simulator_url}/ok.log")
    wrong.close()


@pytest.mark.parametrize(("path", "status"), [("error.log", 500), ("missing.log", 404)])
def test_other_http_errors_keep_the_status(
    client: HttpScanClient, scan_simulator_url: str, path: str, status: int
) -> None:
    """Any other HTTP >= 400 is "error de SCAN" (RF-022)."""
    with pytest.raises(ScanHttpError) as error:
        client.fetch(f"{scan_simulator_url}/{path}")

    assert error.value.status_code == status


def test_blank_body_is_an_empty_response(client: HttpScanClient, scan_simulator_url: str) -> None:
    """A blank body is "respuesta sin datos" (RF-022)."""
    with pytest.raises(ScanEmptyResponse):
        client.fetch(f"{scan_simulator_url}/empty.log")


def test_each_thread_uses_its_own_session(client: HttpScanClient, scan_simulator_url: str) -> None:
    """Sessions are never shared between threads (design: one session per thread)."""
    sessions: list[int] = []

    def download() -> None:
        client.fetch(f"{scan_simulator_url}/ok.log")
        sessions.append(id(client._session()))

    threads = [threading.Thread(target=download) for _ in range(3)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(set(sessions)) == 3


def test_error_text_does_not_expose_credentials(scan_simulator_url: str) -> None:
    """Credentials never appear in the failure text (RF-022)."""
    wrong = HttpScanClient(ScanCredentials(username=USERNAME, password="wrong"), 1)

    with pytest.raises(ScanUnauthorized) as error:
        wrong.fetch(f"{scan_simulator_url}/ok.log")
    wrong.close()

    assert "wrong" not in str(error.value)
