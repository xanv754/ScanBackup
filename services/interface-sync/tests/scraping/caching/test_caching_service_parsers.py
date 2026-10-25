import pytest

from interface_sync.exceptions import ScanHttpError, UnreadablePageError
from interface_sync.scraping.caching.abatvgo import CachingAbatvgoParser
from interface_sync.scraping.caching.akamai import CachingAkamaiParser
from interface_sync.scraping.caching.facebook import CachingFacebookParser
from interface_sync.scraping.caching.google import CachingGoogleParser
from interface_sync.scraping.caching.inter import CachingInterParser
from interface_sync.scraping.caching.netflix import CachingNetflixParser

MENU_URL = "https://scan.example/cgi-bin/chg/trafico-caching.cgi?SUMAS-CACHING.dummy"
SUFFIX = " - Trafico de Red"
LONG_NAME = "Router ANZ-HWDIST-00 (100GE1/1/0.2171 conexión con NODO GOOGLE CACHING ANZ)"

SERVICES = {
    "Google": (CachingGoogleParser, "Suma GOOGLE", 19),
    "Akamai": (CachingAkamaiParser, "Suma AKAMAI", 1),
    "Facebook": (CachingFacebookParser, "Suma FACEBOOK (META)", None),
    "Inter": (CachingInterParser, "ALIANZA INTER", 1),
    "Netflix": (CachingNetflixParser, "Suma NETFLIX", 8),
    "Abatvgo": (CachingAbatvgoParser, "Suma ABATVGO", 6),
}


def service_url(vendor: str) -> str:
    return f"https://scan.example/cgi-bin/chg/trafico-caching-{vendor.lower()}.cgi?{vendor}.dummy"


class FakeFetcher:
    """Serves the registered pages and records every requested URL."""

    def __init__(self, pages: dict[str, str] | None = None) -> None:
        self.pages = pages or {}
        self.requested: list[str] = []

    def fetch_html(self, url: str) -> str:
        self.requested.append(url)
        if url not in self.pages:
            raise ScanHttpError(404)
        return self.pages[url]


def build_entry(label: str, href: str | None, badge: int | None = None) -> str:
    badge_html = f'<span class="badge badge-info right">{badge}</span>' if badge else ""
    anchor_open, anchor_close = (
        (f'<a href="{href}" class="nav-link">', "</a>") if href else ("", "")
    )
    return f'<li class="nav-item">{anchor_open}<i></i><p>{label}{badge_html}</p>{anchor_close}</li>'


def build_menu(
    entries: dict[str, str | None] | None = None,
    with_sidebar: bool = True,
    with_menu: bool = True,
) -> str:
    """Build a menu with every service (Inter nested one level deeper, as in SCAN)."""
    hrefs = {
        vendor: service_url(vendor).removeprefix("https://scan.example") for vendor in SERVICES
    }
    hrefs.update(entries or {})
    flat = "".join(
        build_entry(label, hrefs[vendor], badge)
        for vendor, (_, label, badge) in SERVICES.items()
        if vendor != "Inter"
    )
    inter_label = SERVICES["Inter"][1]
    detail = (
        '<li class="nav-item"><a href="#"><p>CACHING EN DETALLE<i></i></p></a>'
        f'<ul class="nav nav-treeview">{build_entry(inter_label, hrefs["Inter"], 1)}</ul></li>'
    )
    menu_open = '<ul role="menu">' if with_menu else "<ul>"
    sidebar_class = "sidebar" if with_sidebar else "other"
    return (
        f'<html><body><div class="{sidebar_class}"><nav>{menu_open}'
        '<li class="nav-header">CACHING</li>'
        f"{build_entry('Alarmas de Router Disp.', '/alarmas.cgi')}"
        '<li class="nav-item menu-open"><a href="#"><p>Sumatorias<i></i></p></a>'
        f'<ul class="nav nav-treeview">'
        f"{build_entry('Sumatorias Totales', '/cgi-bin/chg/trafico-caching.cgi', 5)}"
        f"{flat}{detail}</ul></li></ul></nav></div></body></html>"
    )


def build_block(title: str | None, href: str | None = "/mrtg/x.html") -> str:
    title_html = f'<li id="subtitulo" class="list-group-item"> {title}\n</li>' if title else ""
    link_html = f'<a href="{href}" target="_blank"><img src="x.png"></a>' if href else ""
    return (
        '<div class="col-sm-12"><ul class="list-group">'
        f'{title_html}<li id="graficas"><center>{link_html}'
        "<br>Max<em>In</em><td>5457.1 Mb/s</td></center></li></ul></div>"
    )


def build_service_page(
    *blocks: str,
    with_content: bool = True,
    with_row: bool = True,
    with_column: bool = True,
) -> str:
    content_tag = "section" if with_content else "article"
    row_open, row_close = ('<div class="row">', "</div>") if with_row else ("", "")
    col_open, col_close = ('<div class="col-md-12"><br>', "</div>") if with_column else ("", "")
    return (
        f'<html><body><{content_tag} class="content">{row_open}{col_open}'
        f"{''.join(blocks)}{col_close}{row_close}</{content_tag}></body></html>"
    )


@pytest.fixture(params=list(SERVICES))
def vendor(request: pytest.FixtureRequest) -> str:
    return request.param


def parse_blocks(vendor: str, blocks: list[str]) -> list:
    fetcher = FakeFetcher({service_url(vendor): build_service_page(*blocks)})
    return SERVICES[vendor][0](fetcher).parse(build_menu(), MENU_URL)


def test_valid_interface_is_fully_extracted(vendor: str) -> None:
    """RF-003: name, scan_url, capacity and vendor come from a regular block."""
    blocks = [build_block(f"{LONG_NAME}{SUFFIX}", "/mrtg/r27421-ge110-2171.html")]

    [interface] = parse_blocks(vendor, blocks)

    assert interface.position == 1
    assert interface.name == LONG_NAME.removeprefix("Router ").upper()
    assert interface.scan_url == "https://scan.example/mrtg/r27421-ge110-2171.log"
    assert interface.capacity_gbps == 100.0
    assert interface.vendor == vendor


def test_only_its_own_service_page_is_downloaded(vendor: str) -> None:
    """RF-003: the other services, sums and alarms of the menu are never downloaded."""
    fetcher = FakeFetcher({service_url(vendor): build_service_page()})

    SERVICES[vendor][0](fetcher).parse(build_menu(), MENU_URL)

    assert fetcher.requested == [service_url(vendor)]


def test_service_is_found_with_a_different_label_case_and_badge(vendor: str) -> None:
    """RF-003: the label match ignores case and the badge counter next to it."""
    label = SERVICES[vendor][1].lower()
    menu = build_menu().replace(SERVICES[vendor][1], label)
    fetcher = FakeFetcher({service_url(vendor): build_service_page()})

    SERVICES[vendor][0](fetcher).parse(menu, MENU_URL)

    assert fetcher.requested == [service_url(vendor)]


def test_service_missing_from_menu_returns_empty_list(vendor: str) -> None:
    """RF-003: a service absent from the menu contributes nothing, like in Bras."""
    label = SERVICES[vendor][1]
    menu = build_menu().replace(label, "OTRO SERVICIO")
    fetcher = FakeFetcher()

    assert SERVICES[vendor][0](fetcher).parse(menu, MENU_URL) == []
    assert fetcher.requested == []


def test_service_entry_without_link_is_ignored(vendor: str) -> None:
    """RF-003: a menu label without `a[href]` has no page to download."""
    menu = build_menu().replace(
        f'<a href="{service_url(vendor).removeprefix("https://scan.example")}" class="nav-link">',
        "<a>",
    )
    fetcher = FakeFetcher()

    assert SERVICES[vendor][0](fetcher).parse(menu, MENU_URL) == []
    assert fetcher.requested == []


def test_service_page_url_is_resolved_against_the_menu_url(vendor: str) -> None:
    """RF-003: a relative menu link becomes an absolute URL."""
    menu = build_menu({vendor: "relative.cgi?x"})
    expected = "https://scan.example/cgi-bin/chg/relative.cgi?x"
    fetcher = FakeFetcher({expected: build_service_page()})

    SERVICES[vendor][0](fetcher).parse(menu, MENU_URL)

    assert fetcher.requested == [expected]


@pytest.mark.parametrize(
    "title",
    [
        "Router ANZ-HWDIST-00 (100GE1) - Tr&aacute;fico de Red",
        "Router ANZ-HWDIST-00 (100GE1) - TRAFICO DE RED",
        "Router ANZ-HWDIST-00 (100GE1) - Trafico de Rd",
        "router anz-hwdist-00 (100ge1) - trafico de red",
        "  Router   ANZ-HWDIST-00   (100GE1)   -   Tráfico  de  Red  ",
        "Router ANZ-HWDIST-00 (100GE1)-Trafico de Red",
        "ANZ-HWDIST-00 (100GE1) - Trafico de Red",
    ],
)
def test_name_ignores_prefix_and_suffix_in_any_format_and_is_uppercase(
    vendor: str, title: str
) -> None:
    """RF-003: prefix and suffix are removed regardless of case, accent or spacing."""
    [interface] = parse_blocks(vendor, [build_block(title)])

    assert " ".join(interface.name.split()) == "ANZ-HWDIST-00 (100GE1)"


def test_title_without_suffix_is_kept_as_an_interface(vendor: str) -> None:
    """RF-003: a non-summary title without the suffix is not silently lost."""
    [interface] = parse_blocks(vendor, [build_block("Router X (100GE1)")])

    assert interface.name == "X (100GE1)"


def test_empty_name_is_kept_as_incomplete_interface(vendor: str) -> None:
    """RF-003/RF-004: a title that is only prefix and suffix leaves `name` as None."""
    [interface] = parse_blocks(vendor, [build_block("Router - Trafico de Red")])

    assert interface.name is None
    assert interface.scan_url is not None


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("Router X (100GE1/1/0.2171 conexión)", 100.0),
        ("Router X (10GE1/0/1)", 10.0),
        ("Router X (10GB GE1/0/1)", 10.0),
        ("Router X (100ge1)", 100.0),
        ("Router X (50|100GE8/0/2)", 100.0),
        ("Router X (Eth-Trunk1 conexión con CDN AKAMAI)", None),
        ("Router X (GE1/0/1)", None),
        ("Router X (10 GE1/0/1)", None),
        ("Router X", None),
    ],
)
def test_capacity_is_read_from_the_port_name(
    vendor: str, title: str, expected: float | None
) -> None:
    """RF-003: the number before `GE`/`GB` is the capacity; otherwise it is not obtainable."""
    [interface] = parse_blocks(vendor, [build_block(f"{title}{SUFFIX}")])

    assert interface.capacity_gbps == expected


@pytest.mark.parametrize(
    "title",
    [
        "Sumatoria GOOGLE CACHING - Tráfico de Red",
        "SUMATORIA FACEBOOK CACHING INTER",
        "  sumatoria  NETFLIX",
        "Router X (100GE1) Sumatoria - Trafico de Red",
    ],
)
def test_summaries_are_skipped_without_consuming_a_position(vendor: str, title: str) -> None:
    """RF-003: any title containing "Sumatoria" is omitted; positions stay consecutive."""
    blocks = [
        build_block(title),
        build_block(f"Router A (100GE1){SUFFIX}"),
        build_block(title),
        build_block(f"Router B (100GE2){SUFFIX}"),
    ]

    interfaces = parse_blocks(vendor, blocks)

    assert [(i.position, i.name) for i in interfaces] == [(1, "A (100GE1)"), (2, "B (100GE2)")]


@pytest.mark.parametrize(
    ("href", "expected"),
    [
        ("/mrtg/r1.html", "https://scan.example/mrtg/r1.log"),
        ("mrtg/r1.html", "https://scan.example/cgi-bin/chg/mrtg/r1.log"),
        ("https://other.example/mrtg/r1.html", "https://other.example/mrtg/r1.log"),
        ("  /mrtg/r1.html  ", "https://scan.example/mrtg/r1.log"),
        ("/mrtg/r1.html?x=1", "https://scan.example/mrtg/r1.log?x=1"),
        ("/mrtg/r1.v2.html", "https://scan.example/mrtg/r1.v2.log"),
        ("/mrtg/a.html/b.html", "https://scan.example/mrtg/a.html/b.log"),
    ],
)
def test_scan_url_is_absolute_and_ends_in_log(vendor: str, href: str, expected: str) -> None:
    """RF-003: the href is resolved against the service page and `.html` becomes `.log`."""
    [interface] = parse_blocks(vendor, [build_block(f"Router A (100GE1){SUFFIX}", href)])

    assert interface.scan_url == expected


@pytest.mark.parametrize("href", ["/mrtg/r1.log", "/mrtg/r1", "/mrtg/r1.htm", "/mrtg/", "#", ""])
def test_href_without_html_extension_leaves_scan_url_empty(vendor: str, href: str) -> None:
    """RF-003/RF-004: an href not ending in `.html` makes the interface incomplete."""
    [interface] = parse_blocks(vendor, [build_block(f"Router A (100GE1){SUFFIX}", href)])

    assert interface.scan_url is None
    assert interface.name == "A (100GE1)"


def test_block_without_link_is_kept_as_incomplete_interface(vendor: str) -> None:
    """RF-003/RF-004: a block with title but no anchor is not discarded."""
    [interface] = parse_blocks(vendor, [build_block(f"Router A (100GE1){SUFFIX}", href=None)])

    assert interface.scan_url is None
    assert interface.name == "A (100GE1)"


def test_block_without_graphs_item_is_kept_as_incomplete_interface(vendor: str) -> None:
    """RF-003/RF-004: a block without `li#graficas` is not discarded."""
    block = (
        f'<div class="col-sm-12"><ul><li id="subtitulo"> Router A (100GE1){SUFFIX}</li></ul></div>'
    )

    [interface] = parse_blocks(vendor, [block])

    assert interface.scan_url is None


def test_block_without_title_is_ignored(vendor: str) -> None:
    """RF-003: a block with no `li#subtitulo` is not an interface."""
    interfaces = parse_blocks(
        vendor, [build_block(None), build_block(f"Router A (100GE1){SUFFIX}")]
    )

    assert [(i.position, i.name) for i in interfaces] == [(1, "A (100GE1)")]


def test_service_page_with_only_summaries_returns_empty_list(vendor: str) -> None:
    """RF-003: a page with only summaries (Facebook today) yields no interfaces, not an error."""
    assert parse_blocks(vendor, [build_block("Sumatoria X CACHING - Tráfico de Red")]) == []


def test_service_page_with_zero_rows_returns_empty_list(vendor: str) -> None:
    """RF-003/RF-006: structure present with zero rows yields an empty listing."""
    assert parse_blocks(vendor, []) == []


def test_dirty_html_is_tolerated(vendor: str) -> None:
    """RF-003: stray `<td>`, unclosed tags and repeated ids do not break the parsing."""
    block = (
        '<div class="col-sm-12"><ul><li id="subtitulo"> Router A (100GE1) - Trafico de Red\n'
        '<li id="graficas"><center><a href="/mrtg/r1.html"><img id="graficas"></a>'
        "<br>Max<em>In</em><td>1 Gb/s</td>&nbsp;<td>2 Gb/s</td></center></ul></div>"
    )

    [interface] = parse_blocks(vendor, [block])

    assert interface.name == "A (100GE1)"
    assert interface.scan_url == "https://scan.example/mrtg/r1.log"


@pytest.mark.parametrize(
    "menu",
    [
        build_menu(with_sidebar=False),
        build_menu(with_menu=False),
        "",
        "plain text, not html",
        "<html><body><h1>Login</h1></body></html>",
    ],
)
def test_unreadable_menu_raises(vendor: str, menu: str) -> None:
    """RF-003: a menu without `div.sidebar > ul[role=menu]` makes the page unreadable."""
    fetcher = FakeFetcher()

    with pytest.raises(UnreadablePageError):
        SERVICES[vendor][0](fetcher).parse(menu, MENU_URL)

    assert fetcher.requested == []


@pytest.mark.parametrize(
    ("page", "missing"),
    [
        (build_service_page(with_content=False), "section.content"),
        (build_service_page(with_row=False), "div.row"),
        (build_service_page(with_column=False), "div.col-md-12"),
        ("", "section.content"),
        ("<html><body><p>Error</p></body></html>", "section.content"),
    ],
)
def test_unreadable_service_page_raises(vendor: str, page: str, missing: str) -> None:
    """RF-003: a service page without its expected structure makes the page unreadable."""
    fetcher = FakeFetcher({service_url(vendor): page})

    with pytest.raises(UnreadablePageError) as error_info:
        SERVICES[vendor][0](fetcher).parse(build_menu(), MENU_URL)

    assert missing in error_info.value.cause


def test_failure_downloading_the_service_page_reaches_the_caller(vendor: str) -> None:
    """RF-003/RF-010: a failing service page fails the whole Caching page; nothing is swallowed."""
    fetcher = FakeFetcher()

    with pytest.raises(ScanHttpError):
        SERVICES[vendor][0](fetcher).parse(build_menu(), MENU_URL)

    assert fetcher.requested == [service_url(vendor)]
