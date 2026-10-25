import re
from urllib.parse import urljoin, urlsplit, urlunsplit

from bs4 import BeautifulSoup, Tag

from interface_sync.exceptions import UnreadablePageError
from interface_sync.models import ScrapedInterface
from interface_sync.scraping.ixp.vendor_extractor import IxpVendorExtractor
from interface_sync.scraping.page_parser import PageParser


class IxpParser(PageParser):
    """Parser of the Ixp layer listing page.

    Structure: `main#main > div.row > div` (one per block) with `li#subtitulo` (title)
    and `li#graficas > a[href]` (link to the traffic page, `.html`). The traffic values
    are read from the `.log` version of that link. Blocks whose title contains
    "Sumatoria" are skipped. Capacity comes from the own port of the interface, which is
    the part of the name before "conexión con" (`100GB Eth-Trunk1.1502`, `100GE1/0/0` and
    `GE1/1/4(10G)` are read; the neighbor device is ignored). The vendor of each interface
    is taken from its name by the injected extractor, since the page has no single vendor.
    """

    MAIN_ID = "main"
    ROW_CLASS = "row"
    TITLE_ID = "subtitulo"
    GRAPHS_ID = "graficas"
    SUMMARY_KEYWORD = "sumatoria"
    PAGE_EXTENSION = ".html"
    TRAFFIC_EXTENSION = ".log"
    TITLE_PREFIX_PATTERN = re.compile(r"^\s*router\s+", re.IGNORECASE)
    TITLE_SUFFIX_PATTERN = re.compile(r"-\s*tr[aá]fico\s+de\s+r(?:ed|d)\s*$", re.IGNORECASE)
    PORT_SEPARATOR_PATTERN = re.compile(r"\bconexi[oó]n\b", re.IGNORECASE)
    CAPACITY_PATTERN = re.compile(r"(\d+)(?:G(?:[EB]|(?=\)))|(?=Eth-Trunk))", re.IGNORECASE)

    def __init__(self, vendor_extractor: IxpVendorExtractor) -> None:
        """Set the extractor that obtains the vendor of each interface from its name."""
        self._vendor_extractor = vendor_extractor

    def parse(self, html: str, page_url: str) -> list[ScrapedInterface]:
        """Return every Ixp interface in page order, without summaries."""
        listing = self._find_listing(BeautifulSoup(html, "html5lib"))
        interfaces: list[ScrapedInterface] = []
        for block in listing.find_all("div", recursive=False):
            title_element = block.find("li", id=self.TITLE_ID)
            if title_element is None:
                continue
            title = " ".join(title_element.get_text().split())
            if self.SUMMARY_KEYWORD in title.lower():
                continue
            name = self._extract_name(title)
            interfaces.append(
                ScrapedInterface(
                    position=len(interfaces) + 1,
                    name=name,
                    scan_url=self._extract_scan_url(block, page_url),
                    capacity_gbps=self._extract_capacity_gbps(name),
                    vendor=self._vendor_extractor.extract(name),
                )
            )
        return interfaces

    def _find_listing(self, soup: BeautifulSoup) -> Tag:
        """Return the `div.row` that holds the blocks; raise `UnreadablePageError` if absent."""
        main = soup.find(id=self.MAIN_ID)
        if main is None:
            raise UnreadablePageError(f"main#{self.MAIN_ID}")
        listing = main.find("div", class_=self.ROW_CLASS)
        if listing is None:
            raise UnreadablePageError(f"div.{self.ROW_CLASS}")
        return listing

    def _extract_name(self, title: str) -> str | None:
        """Remove the fixed prefix and suffix of the title and return it in uppercase."""
        name = self.TITLE_PREFIX_PATTERN.sub("", title)
        name = self.TITLE_SUFFIX_PATTERN.sub("", name).strip()
        return name.upper() or None

    def _extract_scan_url(self, block: Tag, page_url: str) -> str | None:
        """Return the absolute `.log` URL of the block, or `None` without a `.html` link."""
        graphs = block.find("li", id=self.GRAPHS_ID)
        anchor = graphs.find("a", href=True) if graphs is not None else None
        if anchor is None:
            return None
        parts = urlsplit(urljoin(page_url, str(anchor["href"]).strip()))
        if not parts.path.endswith(self.PAGE_EXTENSION):
            return None
        traffic_path = parts.path.removesuffix(self.PAGE_EXTENSION) + self.TRAFFIC_EXTENSION
        return urlunsplit(parts._replace(path=traffic_path))

    def _extract_capacity_gbps(self, name: str | None) -> float | None:
        """Return the number before `GE`, `GB`, `G)` or `Eth-Trunk` in the own port, or `None`."""
        if not name:
            return None
        own_port = self.PORT_SEPARATOR_PATTERN.split(name, maxsplit=1)[0]
        match = self.CAPACITY_PATTERN.search(own_port)
        return float(match.group(1)) if match else None
