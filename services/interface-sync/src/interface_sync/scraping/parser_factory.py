from typing import ClassVar

from interface_sync.exceptions import UnsupportedPageError
from interface_sync.models import PageConfig
from interface_sync.scraping.borde.huawei import BordeHuaweiParser
from interface_sync.scraping.borde.juniper import BordeJuniperParser
from interface_sync.scraping.page_parser import PageParser


class PageParserFactory:
    """Creates the parser that matches the layer and vendor of a configured page."""

    PARSERS: ClassVar[dict[tuple[str, str], type[PageParser]]] = {
        ("Borde", "Huawei"): BordeHuaweiParser,
        ("Borde", "Juniper"): BordeJuniperParser,
    }

    def create(self, page: PageConfig) -> PageParser:
        """Return a parser for the page; raise `UnsupportedPageError` if none is registered."""
        parser_class = self.PARSERS.get((page.layer, page.vendor))
        if parser_class is None:
            raise UnsupportedPageError(page.layer, page.vendor)
        return parser_class()
