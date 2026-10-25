import re
from urllib.parse import urljoin, urlsplit, urlunsplit

from bs4 import BeautifulSoup, Tag

from interface_sync.exceptions import UnreadablePageError
from interface_sync.models import ScrapedInterface
from interface_sync.scraping.html_fetcher import HtmlFetcher
from interface_sync.scraping.page_parser import PageParser


class CachingAbatvgoParser(PageParser):
    """Parser of the Caching layer interfaces of the Abatvgo service ("SUMA ABATVGO").

    The configured page is only the menu: `div.sidebar > ul[role=menu]`, where the service
    is a nested `li` whose `a > p` label is "SUMA ABATVGO" (followed by a badge counter). Its
    link leads to the service page, which is downloaded and read:
    `section.content > div.row > div.col-md-12 > div` (one per block) with `li#subtitulo`
    (title) and `li#graficas > a[href]` (link to the traffic page, `.html`). Titles that
    contain "Sumatoria" are skipped. If the service is not in the menu, it has no
    interfaces. Capacity comes from the port name (`100GE1/1/0.2171` means 100 Gbps).
    """

    VENDOR = "ABATVGO"
    SIDEBAR_CLASS = "sidebar"
    MENU_ROLE = "menu"
    MENU_LABEL_PATTERN = re.compile(r"^SUMA ABATVGO$", re.IGNORECASE)
    BADGE_CLASS = "badge"
    CONTENT_CLASS = "content"
    ROW_CLASS = "row"
    COLUMN_CLASS = "col-md-12"
    TITLE_ID = "subtitulo"
    GRAPHS_ID = "graficas"
    SUMMARY_KEYWORD = "sumatoria"
    PAGE_EXTENSION = ".html"
    TRAFFIC_EXTENSION = ".log"
    TITLE_PREFIX_PATTERN = re.compile(r"^\s*router\s+", re.IGNORECASE)
    TITLE_SUFFIX_PATTERN = re.compile(r"-\s*tr[aá]fico\s+de\s+r(?:ed|d)\s*$", re.IGNORECASE)
    CAPACITY_PATTERN = re.compile(r"(\d+)G[EB]")

    def __init__(self, fetcher: HtmlFetcher) -> None:
        """Set the downloader used to fetch the service page."""
        self._fetcher = fetcher

    def parse(self, html: str, page_url: str) -> list[ScrapedInterface]:
        """Return every Abatvgo interface of the service page linked in the menu."""
        service_page_url = self._find_service_page_url(html, page_url)
        if service_page_url is None:
            return []
        return self._parse_service_page(
            self._fetcher.fetch_html(service_page_url), service_page_url
        )

    def _find_service_page_url(self, html: str, page_url: str) -> str | None:
        """Return the absolute URL of the service page, or `None` if the menu lacks it."""
        soup = BeautifulSoup(html, "html5lib")
        sidebar = soup.find("div", class_=self.SIDEBAR_CLASS)
        if sidebar is None:
            raise UnreadablePageError(f"div.{self.SIDEBAR_CLASS}")
        menu = sidebar.find("ul", attrs={"role": self.MENU_ROLE})
        if menu is None:
            raise UnreadablePageError(f"ul[role={self.MENU_ROLE}]")
        for item in menu.find_all("li"):
            anchor = item.find("a", href=True, recursive=False)
            if anchor is None:
                continue
            if self.MENU_LABEL_PATTERN.match(self._read_label(anchor)):
                return urljoin(page_url, str(anchor["href"]).strip())
        return None

    def _read_label(self, anchor: Tag) -> str:
        """Return the whitespace-normalized text of the `p` label, without its badge."""
        label = anchor.find("p")
        if label is None:
            return ""
        for badge in label.find_all(class_=self.BADGE_CLASS):
            badge.decompose()
        return " ".join(label.get_text().split())

    def _parse_service_page(self, html: str, page_url: str) -> list[ScrapedInterface]:
        """Return the interfaces of the service page, without summaries."""
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
                    vendor=self.VENDOR,
                )
            )
        return interfaces

    def _find_listing(self, soup: BeautifulSoup) -> Tag:
        """Return the `div.col-md-12` with the blocks; raise `UnreadablePageError` if absent."""
        content = soup.find("section", class_=self.CONTENT_CLASS)
        if content is None:
            raise UnreadablePageError(f"section.{self.CONTENT_CLASS}")
        row = content.find("div", class_=self.ROW_CLASS)
        if row is None:
            raise UnreadablePageError(f"div.{self.ROW_CLASS}")
        listing = row.find("div", class_=self.COLUMN_CLASS)
        if listing is None:
            raise UnreadablePageError(f"div.{self.COLUMN_CLASS}")
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
        """Return the number before `GE`/`GB` in the name, or `None` if there is none."""
        match = self.CAPACITY_PATTERN.search(name) if name else None
        return float(match.group(1)) if match else None
