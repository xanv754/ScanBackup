from interface_sync.models import ScrapedInterface
from interface_sync.scraping.caching.abatvgo import CachingAbatvgoParser
from interface_sync.scraping.caching.akamai import CachingAkamaiParser
from interface_sync.scraping.caching.facebook import CachingFacebookParser
from interface_sync.scraping.caching.google import CachingGoogleParser
from interface_sync.scraping.caching.inter import CachingInterParser
from interface_sync.scraping.caching.netflix import CachingNetflixParser
from interface_sync.scraping.html_fetcher import HtmlFetcher
from interface_sync.scraping.page_parser import PageParser


class CachingParser(PageParser):
    """Parser of the Caching layer page: joins the interfaces of every caching service.

    The configured page is only a menu. Each service parser finds its own page in that menu
    and reads it on its own, so a change in one service does not touch the others. Positions
    are renumbered across the whole page.
    """

    def __init__(self, fetcher: HtmlFetcher) -> None:
        """Create the parsers of every caching service, in the order they are returned."""
        self._service_parsers: tuple[PageParser, ...] = (
            CachingGoogleParser(fetcher),
            CachingAkamaiParser(fetcher),
            CachingFacebookParser(fetcher),
            CachingInterParser(fetcher),
            CachingNetflixParser(fetcher),
            CachingAbatvgoParser(fetcher),
        )

    def parse(self, html: str, page_url: str) -> list[ScrapedInterface]:
        """Return the interfaces of every service in order, numbered across the page."""
        interfaces: list[ScrapedInterface] = []
        for service_parser in self._service_parsers:
            for interface in service_parser.parse(html, page_url):
                interfaces.append(
                    interface.model_copy(update={"position": len(interfaces) + 1})
                )
        return interfaces
