import re
from urllib.parse import urljoin, urlsplit, urlunsplit

from bs4 import BeautifulSoup, Tag

from interface_sync.exceptions import UnreadablePageError
from interface_sync.models import ScrapedInterface
from interface_sync.scraping.html_fetcher import HtmlFetcher
from interface_sync.scraping.page_parser import PageParser


class BrasDownlinkParser(PageParser):
    """Parser of the Bras layer interfaces of type Downlink ("DOWNLINK POR BRAS").

    The configured page is only the menu: `div.sidebar > ul[role=menu]`, with one
    `li.nav-item.menu` per BRAS group (`ANZ-BRAS`) whose submenu "DOWNLINK POR BRAS" links to
    one page per device (`ANZ-BRAS-00`). Each of those pages is downloaded and read:
    `section.content > div.row > div.col-md-12 > div` (one per block) with `li#subtitulo`
    (title) and `li#graficas > a[href]` (link to the traffic page, `.html`). Titles that
    contain "Sumatoria" are skipped. Capacity comes from the port name (`10GB GE1/0/1`).
    """

    VENDOR = "DOWNLINK"
    SIDEBAR_CLASS = "sidebar"
    MENU_ROLE = "menu"
    GROUP_CLASSES = ("nav-item", "menu")
    GROUP_LABEL_PATTERN = re.compile(r"^[A-Z]{3}-BRAS$")
    SECTION_LABEL = "DOWNLINK POR BRAS"
    CONTENT_CLASS = "content"
    ROW_CLASS = "row"
    COLUMN_CLASS = "col-md-12"
    TITLE_ID = "subtitulo"
    GRAPHS_ID = "graficas"
    SUMMARY_KEYWORD = "sumatoria"
    PAGE_EXTENSION = ".html"
    TRAFFIC_EXTENSION = ".log"
    TITLE_SUFFIX_PATTERN = re.compile(r"-\s*tr[aá]fico\s+de\s+red\s*$", re.IGNORECASE)
    CAPACITY_PATTERN = re.compile(r"(\d+)GB")

    def __init__(self, fetcher: HtmlFetcher) -> None:
        """Set the downloader used to fetch the page of each BRAS device."""
        self._fetcher = fetcher

    def parse(self, html: str, page_url: str) -> list[ScrapedInterface]:
        """Return every Downlink interface of the BRAS pages linked in the menu."""
        interfaces: list[ScrapedInterface] = []
        for device_page_url in self._find_device_page_urls(html, page_url):
            device_html = self._fetcher.fetch_html(device_page_url)
            interfaces.extend(
                self._parse_device_page(device_html, device_page_url, len(interfaces))
            )
        return interfaces

    def _find_device_page_urls(self, html: str, page_url: str) -> list[str]:
        """Return the absolute URLs of the device pages listed under "DOWNLINK POR BRAS"."""
        soup = BeautifulSoup(html, "html5lib")
        sidebar = soup.find("div", class_=self.SIDEBAR_CLASS)
        if sidebar is None:
            raise UnreadablePageError(f"div.{self.SIDEBAR_CLASS}")
        menu = sidebar.find("ul", attrs={"role": self.MENU_ROLE})
        if menu is None:
            raise UnreadablePageError(f"ul[role={self.MENU_ROLE}]")
        device_page_urls: list[str] = []
        for group in menu.find_all("li", recursive=False):
            group_label = self._read_label(group)
            if not all(css in group.get("class", []) for css in self.GROUP_CLASSES):  # type: ignore
                continue
            if not self.GROUP_LABEL_PATTERN.match(group_label):
                continue
            device_page_urls.extend(
                self._read_section_urls(group, group_label, page_url)
            )
        return device_page_urls

    def _read_section_urls(
        self, group: Tag, group_label: str, page_url: str
    ) -> list[str]:
        """Return the device page URLs of the "DOWNLINK POR BRAS" section of a BRAS group."""
        group_submenu = group.find("ul", recursive=False)
        if group_submenu is None:
            return []
        device_label_pattern = re.compile(rf"^{re.escape(group_label)}-\d{{2}}$")
        urls: list[str] = []
        for section in group_submenu.find_all("li", recursive=False):
            if self.SECTION_LABEL not in self._read_label(section).upper():
                continue
            section_submenu = section.find("ul", recursive=False)
            if section_submenu is None:
                continue
            for device in section_submenu.find_all("li", recursive=False):
                anchor = device.find("a", href=True, recursive=False)
                if anchor is None or not device_label_pattern.match(
                    self._read_label(device)
                ):
                    continue
                urls.append(urljoin(page_url, str(anchor["href"]).strip()))
        return urls

    def _read_label(self, item: Tag) -> str:
        """Return the whitespace-normalized text of the `p` label of a menu item."""
        label = item.find("p")
        return " ".join(label.get_text().split()) if label is not None else ""

    def _parse_device_page(
        self, html: str, page_url: str, already_found: int
    ) -> list[ScrapedInterface]:
        """Return the interfaces of one device page, numbered after `already_found`."""
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
                    position=already_found + len(interfaces) + 1,
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
        """Remove the fixed suffix of the title and return it in uppercase."""
        name = self.TITLE_SUFFIX_PATTERN.sub("", title).strip()
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
        traffic_path = (
            parts.path.removesuffix(self.PAGE_EXTENSION) + self.TRAFFIC_EXTENSION
        )
        return urlunsplit(parts._replace(path=traffic_path))

    def _extract_capacity_gbps(self, name: str | None) -> float | None:
        """Return the number before `GB` in the name, or `None` if the name has no such number."""
        match = self.CAPACITY_PATTERN.search(name) if name else None
        return float(match.group(1)) if match else None
