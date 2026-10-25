from collections.abc import Callable

from interface_sync.exceptions import UnsupportedPageError
from interface_sync.models import PageConfig
from interface_sync.scraping.borde.huawei import BordeHuaweiParser
from interface_sync.scraping.borde.juniper import BordeJuniperParser
from interface_sync.scraping.bras.bras_parser import BrasParser
from interface_sync.scraping.caching.caching_parser import CachingParser
from interface_sync.scraping.dint.huawei import DintHuaweiParser
from interface_sync.scraping.html_fetcher import HtmlFetcher
from interface_sync.scraping.page_parser import PageParser


class PageParserFactory:
    """Creates the parser that matches the layer and vendor of a configured page.

    Parsers of layers whose configured page only links to other pages (Bras, Caching)
    receive the downloader of those pages.
    """

    def __init__(self, fetcher: HtmlFetcher) -> None:
        """Register the parser builders of every supported layer and vendor."""
        self._builders: dict[tuple[str, str], Callable[[], PageParser]] = {
            ("Borde", "Huawei"): BordeHuaweiParser,
            ("Borde", "Juniper"): BordeJuniperParser,
            ("Bras", "Undefined"): lambda: BrasParser(fetcher),
            ("Caching", "Undefined"): lambda: CachingParser(fetcher),
            ("Dint", "Huawei"): DintHuaweiParser,
        }

    def create(self, page: PageConfig) -> PageParser:
        """Return a parser for the page; raise `UnsupportedPageError` if none is registered."""
        builder = self._builders.get((page.layer, page.vendor))
        if builder is None:
            raise UnsupportedPageError(page.layer, page.vendor)
        return builder()
