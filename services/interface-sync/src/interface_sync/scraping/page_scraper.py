from interface_sync.models import PageConfig, ScrapedInterface
from interface_sync.scraping.parser_factory import PageParserFactory
from interface_sync.scraping.scan_client import ScanClient


class PageScraper:
    """Obtains the interfaces of a configured SCAN page (RF-003).

    It neither logs nor stores anything: any `PageFetchError` reaches the caller, which
    marks the page as failed using the error `cause`.
    """

    def __init__(self, client: ScanClient, parser_factory: PageParserFactory) -> None:
        """Set the HTTP client and the factory that picks the parser of each page."""
        self._client = client
        self._parser_factory = parser_factory

    def scrape(self, page: PageConfig) -> list[ScrapedInterface]:
        """Download the page and return its interfaces in page order."""
        parser = self._parser_factory.create(page)
        html = self._client.fetch_html(page.url)
        return parser.parse(html, page.url)
