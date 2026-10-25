from unittest.mock import Mock

import pytest

from interface_sync.exceptions import ScanConnectionError, UnsupportedPageError
from interface_sync.models import PageConfig, ScrapedInterface
from interface_sync.scraping import PageParserFactory, PageScraper, ScanClient

URL = "https://scan.example/page.cgi"


@pytest.fixture
def client() -> Mock:
    return Mock(spec=ScanClient)


def test_scrape_downloads_and_parses_the_page(client: Mock) -> None:
    """RF-003: the scraper fetches the configured URL and returns the parsed interfaces."""
    expected = [ScrapedInterface(position=1, name="X", scan_url="u", capacity_gbps=1.0)]
    parser = Mock()
    parser.parse.return_value = expected
    factory = Mock(spec=PageParserFactory)
    factory.create.return_value = parser
    client.fetch_html.return_value = "<html></html>"
    page = PageConfig(layer="borde", vendor="huawei", url=URL)

    result = PageScraper(client, factory).scrape(page)

    assert result == expected
    client.fetch_html.assert_called_once_with(URL)
    parser.parse.assert_called_once_with("<html></html>", URL)


def test_unsupported_page_fails_before_any_request(client: Mock) -> None:
    """RF-003: no SCAN request is made when the layer/vendor has no parser."""
    page = PageConfig(layer="rai", vendor="juniper", url=URL)

    with pytest.raises(UnsupportedPageError):
        PageScraper(client, PageParserFactory(client)).scrape(page)

    client.fetch_html.assert_not_called()


def test_download_failure_reaches_the_caller(client: Mock) -> None:
    """RF-003/RF-010: fetch errors are not swallowed; the caller marks the page as failed."""
    client.fetch_html.side_effect = ScanConnectionError()
    page = PageConfig(layer="borde", vendor="huawei", url=URL)

    with pytest.raises(ScanConnectionError):
        PageScraper(client, PageParserFactory(client)).scrape(page)
