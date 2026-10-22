from unittest.mock import Mock

import pytest
import requests

from interface_sync.exceptions import (
    ScanConnectionError,
    ScanHttpError,
    ScanTimeoutError,
    ScanUnauthorizedError,
)
from interface_sync.models import ScanCredentials
from interface_sync.scraping import ScanClient

PAGE_URL = "https://scan.example/page.cgi"


@pytest.fixture
def session() -> Mock:
    return Mock(spec=requests.Session)


@pytest.fixture
def client(session: Mock) -> ScanClient:
    return ScanClient(ScanCredentials(username="operator", password="secret"), session)


def build_response(status_code: int, text: str = "") -> Mock:
    response = Mock(spec=requests.Response)
    response.status_code = status_code
    response.text = text
    return response


def test_session_uses_basic_auth_and_disables_tls_verification(session: Mock) -> None:
    """RF-003: basic authentication and no TLS verification (self-signed certificate)."""
    ScanClient(ScanCredentials(username="operator", password="secret"), session)

    assert session.auth == ("operator", "secret")
    assert session.verify is False


def test_fetch_returns_page_body(client: ScanClient, session: Mock) -> None:
    """RF-003: a successful response returns its HTML."""
    session.get.return_value = build_response(200, "<html></html>")

    assert client.fetch_html(PAGE_URL) == "<html></html>"


def test_fetch_sends_timeout(client: ScanClient, session: Mock) -> None:
    """RF-003: every request has a timeout."""
    session.get.return_value = build_response(200)

    client.fetch_html(PAGE_URL)

    assert session.get.call_args.kwargs["timeout"] == 30


def test_timeout_maps_to_timeout_error(client: ScanClient, session: Mock) -> None:
    """RF-003: requests.Timeout means "tiempo de espera agotado"."""
    session.get.side_effect = requests.Timeout()

    with pytest.raises(ScanTimeoutError) as error_info:
        client.fetch_html(PAGE_URL)

    assert error_info.value.cause == "tiempo de espera agotado"


def test_connect_timeout_is_a_timeout_not_a_connection_error(
    client: ScanClient, session: Mock
) -> None:
    """RF-003: ConnectTimeout is both Timeout and ConnectionError; Timeout must win."""
    session.get.side_effect = requests.ConnectTimeout()

    with pytest.raises(ScanTimeoutError):
        client.fetch_html(PAGE_URL)


def test_connection_failure_maps_to_connection_error(client: ScanClient, session: Mock) -> None:
    """RF-003: requests.ConnectionError means "sin conexión a SCAN"."""
    session.get.side_effect = requests.ConnectionError()

    with pytest.raises(ScanConnectionError) as error_info:
        client.fetch_html(PAGE_URL)

    assert error_info.value.cause == "sin conexión a SCAN"


def test_http_401_maps_to_unauthorized_error(client: ScanClient, session: Mock) -> None:
    """RF-003: HTTP 401 means "credenciales rechazadas"."""
    session.get.return_value = build_response(401)

    with pytest.raises(ScanUnauthorizedError) as error_info:
        client.fetch_html(PAGE_URL)

    assert error_info.value.cause == "credenciales rechazadas"


@pytest.mark.parametrize("status_code", [400, 403, 404, 500, 503])
def test_other_http_errors_map_to_http_error(
    client: ScanClient, session: Mock, status_code: int
) -> None:
    """RF-003: any other HTTP status >= 400 means "error de SCAN"."""
    session.get.return_value = build_response(status_code)

    with pytest.raises(ScanHttpError) as error_info:
        client.fetch_html(PAGE_URL)

    assert error_info.value.status_code == status_code
    assert str(status_code) in error_info.value.cause


@pytest.mark.parametrize("status_code", [200, 204, 301, 399])
def test_statuses_below_400_are_not_errors(
    client: ScanClient, session: Mock, status_code: int
) -> None:
    """RF-003: only statuses >= 400 are failures."""
    session.get.return_value = build_response(status_code, "body")

    assert client.fetch_html(PAGE_URL) == "body"


def test_context_manager_closes_session(session: Mock) -> None:
    """RF-003: the session is released when the client is used in a with block."""
    with ScanClient(ScanCredentials(username="operator", password="secret"), session):
        pass

    session.close.assert_called_once()


def test_same_session_is_reused_between_pages(client: ScanClient, session: Mock) -> None:
    """RF-003: one session is reused for every page."""
    session.get.return_value = build_response(200)

    client.fetch_html(PAGE_URL)
    client.fetch_html(PAGE_URL + "?other")

    assert session.get.call_count == 2
