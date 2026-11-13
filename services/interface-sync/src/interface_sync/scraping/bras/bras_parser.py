from interface_sync.models import ScrapedInterface
from interface_sync.scraping.bras.downlink import BrasDownlinkParser
from interface_sync.scraping.bras.uplink import BrasUplinkParser
from interface_sync.scraping.html_fetcher import HtmlFetcher
from interface_sync.scraping.page_parser import PageParser


class BrasParser(PageParser):
    """Parser of the Bras layer: joins the Uplink and the Downlink interfaces.

    It holds no scraping logic. Each direction reads the menu page on its own, so a change
    in the HTML of one does not affect the other. Positions are renumbered over the whole
    listing, Uplink first.
    """

    def __init__(self, fetcher: HtmlFetcher) -> None:
        """Create the Uplink and Downlink parsers with the downloader of device pages."""
        self._direction_parsers: tuple[PageParser, ...] = (
            BrasUplinkParser(fetcher),
            BrasDownlinkParser(fetcher),
        )

    def parse(self, html: str, page_url: str) -> list[ScrapedInterface]:
        """Return the Uplink and then the Downlink interfaces, numbered from 1."""
        interfaces: list[ScrapedInterface] = []
        for direction_parser in self._direction_parsers:
            for interface in direction_parser.parse(html, page_url):
                interfaces.append(interface.model_copy(update={"position": len(interfaces) + 1}))
        return interfaces
