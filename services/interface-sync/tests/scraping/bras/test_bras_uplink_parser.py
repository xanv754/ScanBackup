import pytest

from interface_sync.exceptions import ScanHttpError, UnreadablePageError
from interface_sync.scraping.bras.uplink import BrasUplinkParser

MENU_URL = "https://scan.example/cgi-bin/bras/captura-ip-bras.cgi?IP-CAPTURADAS-SUMA-BRAS.dummy"
SUFFIX = " - Trafico de Red"
ANZ_00_URL = "https://scan.example/cgi-bin/bras/uplink-bras-anz.cgi?UPLINK-ANZ-BRAS-00.dummy"
ANZ_02_URL = "https://scan.example/cgi-bin/bras/uplink-bras-anz.cgi?UPLINK-ANZ-BRAS-02.dummy"
BOL_01_URL = "https://scan.example/cgi-bin/bras/uplink-bras-bol.cgi?UPLINK-BOL-BRAS-01.dummy"


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


def build_entry(label: str, href: str | None) -> str:
    anchor_open, anchor_close = (
        (f'<a href="{href}" class="nav-link">', "</a>") if href else ("", "")
    )
    return f'<li class="nav-item">{anchor_open}<i></i><p>{label}</p>{anchor_close}</li>'


def build_section(title: str, entries: list[tuple[str, str | None]]) -> str:
    items = "".join(build_entry(label, href) for label, href in entries)
    return (
        f'<li class="nav-item"><a href="#" class="nav-link"><p>{title}<i></i></p></a>'
        f'<ul class="nav nav-treeview">{items}</ul></li>'
    )


def build_group(
    label: str,
    uplink: list[tuple[str, str | None]] | None = None,
    downlink: list[tuple[str, str | None]] | None = None,
    css_class: str = "nav-item menu",
) -> str:
    sections = [
        build_entry("Disp. X-BRAS-00", "/status.html"),
        build_entry("Sumatorias UPLINK", "/cgi-bin/bras/uplink-bras.cgi?UPLINK-BRAS.dummy"),
        build_entry("Sumatorias DOWNLINK", "/cgi-bin/bras/downlink-bras.cgi?DOWNLINK-BRAS.dummy"),
        build_section("POOLS POR BRAS", [(f"{label}-00", "/cgi-bin/bras/pool.cgi?POOL.dummy")]),
    ]
    if uplink is not None:
        sections.append(build_section("UPLINK POR BRAS", uplink))
    if downlink is not None:
        sections.append(build_section("DOWNLINK POR BRAS", downlink))
    return (
        f'<li class="{css_class}"><a href="#" class="nav-link"><p>{label}<i></i></p></a>'
        f'<ul class="nav nav-treeview">{"".join(sections)}</ul></li>'
    )


def build_menu(*groups: str, with_sidebar: bool = True, with_menu: bool = True) -> str:
    menu_open, menu_close = ('<ul role="menu">', "</ul>") if with_menu else ("<ul>", "</ul>")
    sidebar_class = "sidebar" if with_sidebar else "other"
    return (
        f'<html><body><div class="{sidebar_class}"><nav>{menu_open}'
        '<li class="nav-header">CAPTURA IP</li>'
        '<li class="nav-item"><a href="#"><p>Sumatorias</p></a></li>'
        f"{''.join(groups)}{menu_close}</nav></div></body></html>"
    )


def build_block(title: str | None, href: str | None = "/mrtg/x.html") -> str:
    title_html = f'<li id="subtitulo" class="list-group-item"> {title}\n</li>' if title else ""
    link_html = f'<a href="{href}" target="_blank"><img src="x.png"></a>' if href else ""
    return (
        '<div class="col-sm-12"><ul class="list-group">'
        f'{title_html}<li id="graficas"><center>{link_html}'
        "<br>Max<em>In</em><td>5457.1 Mb/s</td></center></li></ul></div>"
    )


def build_device_page(
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


def menu_with_anz_00() -> str:
    return build_menu(
        build_group(
            "ANZ-BRAS",
            uplink=[("ANZ-BRAS-00", "/cgi-bin/bras/uplink-bras-anz.cgi?UPLINK-ANZ-BRAS-00.dummy")],
        )
    )


def parse_one_page(blocks: list[str]) -> list:
    fetcher = FakeFetcher({ANZ_00_URL: build_device_page(*blocks)})
    return BrasUplinkParser(fetcher).parse(menu_with_anz_00(), MENU_URL)


def test_valid_interface_is_fully_extracted() -> None:
    """RF-003: name, scan_url, capacity and vendor come from a regular block."""
    blocks = [build_block(f"ANZ-BRAS-00 - (10GB GE1/0/1){SUFFIX}", "/mrtg/r27429-ge101.html")]

    [interface] = parse_one_page(blocks)

    assert interface.position == 1
    assert interface.name == "ANZ-BRAS-00 - (10GB GE1/0/1)"
    assert interface.scan_url == "https://scan.example/mrtg/r27429-ge101.log"
    assert interface.capacity_gbps == 10.0
    assert interface.vendor == "UPLINK"


def test_device_pages_are_fetched_in_menu_order_with_absolute_urls() -> None:
    """RF-003: every device page of every BRAS group is downloaded, in menu order."""
    menu = build_menu(
        build_group(
            "ANZ-BRAS",
            uplink=[
                ("ANZ-BRAS-00", "/cgi-bin/bras/uplink-bras-anz.cgi?UPLINK-ANZ-BRAS-00.dummy"),
                ("ANZ-BRAS-02", "/cgi-bin/bras/uplink-bras-anz.cgi?UPLINK-ANZ-BRAS-02.dummy"),
            ],
        ),
        build_group(
            "BOL-BRAS",
            uplink=[("BOL-BRAS-01", "/cgi-bin/bras/uplink-bras-bol.cgi?UPLINK-BOL-BRAS-01.dummy")],
        ),
    )
    page = build_device_page(build_block(f"X (10GB GE1/0/1){SUFFIX}"))
    fetcher = FakeFetcher({ANZ_00_URL: page, ANZ_02_URL: page, BOL_01_URL: page})

    interfaces = BrasUplinkParser(fetcher).parse(menu, MENU_URL)

    assert fetcher.requested == [ANZ_00_URL, ANZ_02_URL, BOL_01_URL]
    assert [interface.position for interface in interfaces] == [1, 2, 3]


def test_only_its_own_direction_is_followed() -> None:
    """RF-003: Downlink, Sumatorias, Pools and Disp. entries are never downloaded."""
    downlink_url = (
        "https://scan.example/cgi-bin/bras/downlink-bras-anz.cgi?DOWNLINK-ANZ-BRAS-00.dummy"
    )
    menu = build_menu(
        build_group(
            "ANZ-BRAS",
            uplink=[("ANZ-BRAS-00", "/cgi-bin/bras/uplink-bras-anz.cgi?UPLINK-ANZ-BRAS-00.dummy")],
            downlink=[
                ("ANZ-BRAS-00", "/cgi-bin/bras/downlink-bras-anz.cgi?DOWNLINK-ANZ-BRAS-00.dummy")
            ],
        )
    )
    fetcher = FakeFetcher({ANZ_00_URL: build_device_page(), downlink_url: build_device_page()})

    BrasUplinkParser(fetcher).parse(menu, MENU_URL)

    assert fetcher.requested == [ANZ_00_URL]


def test_interfaces_of_different_devices_keep_consecutive_positions() -> None:
    """RF-003: positions continue from one device page to the next."""
    menu = build_menu(
        build_group(
            "ANZ-BRAS",
            uplink=[
                ("ANZ-BRAS-00", "/cgi-bin/bras/uplink-bras-anz.cgi?UPLINK-ANZ-BRAS-00.dummy"),
                ("ANZ-BRAS-02", "/cgi-bin/bras/uplink-bras-anz.cgi?UPLINK-ANZ-BRAS-02.dummy"),
            ],
        )
    )
    first = build_device_page(
        build_block(f"A (10GB GE1){SUFFIX}"), build_block(f"B (10GB GE2){SUFFIX}")
    )
    second = build_device_page(build_block(f"C (10GB GE3){SUFFIX}"))
    fetcher = FakeFetcher({ANZ_00_URL: first, ANZ_02_URL: second})

    interfaces = BrasUplinkParser(fetcher).parse(menu, MENU_URL)

    assert [(i.position, i.name) for i in interfaces] == [
        (1, "A (10GB GE1)"),
        (2, "B (10GB GE2)"),
        (3, "C (10GB GE3)"),
    ]


@pytest.mark.parametrize(
    "group",
    [
        build_group("ANZ-BRAS", uplink=[("ANZ-BRAS-00", "/x.cgi")], css_class="nav-item"),
        build_group("ANZ-BRAS", uplink=[("ANZ-BRAS-00", "/x.cgi")], css_class="menu"),
        build_group("ANZ-BRAS-1", uplink=[("ANZ-BRAS-1-00", "/x.cgi")]),
        build_group("anz-bras", uplink=[("anz-bras-00", "/x.cgi")]),
        build_group("ANZ", uplink=[("ANZ-00", "/x.cgi")]),
    ],
)
def test_groups_that_are_not_bras_devices_are_ignored(group: str) -> None:
    """RF-003: only `li.nav-item.menu` entries labeled `XXX-BRAS` are followed."""
    fetcher = FakeFetcher()

    interfaces = BrasUplinkParser(fetcher).parse(build_menu(group), MENU_URL)

    assert interfaces == []
    assert fetcher.requested == []


@pytest.mark.parametrize(
    "device",
    [
        ("ANZ-BRAS-0", "/x.cgi"),
        ("ANZ-BRAS-000", "/x.cgi"),
        ("BOL-BRAS-00", "/x.cgi"),
        ("ANZ-BRAS-00", None),
    ],
)
def test_devices_with_unexpected_label_or_without_link_are_ignored(
    device: tuple[str, str | None],
) -> None:
    """RF-003: a device entry needs the group label plus two digits, and a link."""
    menu = build_menu(build_group("ANZ-BRAS", uplink=[device]))
    fetcher = FakeFetcher()

    assert BrasUplinkParser(fetcher).parse(menu, MENU_URL) == []
    assert fetcher.requested == []


def test_group_without_the_direction_section_is_skipped() -> None:
    """RF-003: a BRAS group with no section of this direction contributes nothing."""
    menu = build_menu(build_group("ANZ-BRAS", downlink=[("ANZ-BRAS-00", "/x.cgi")]))
    fetcher = FakeFetcher()

    assert BrasUplinkParser(fetcher).parse(menu, MENU_URL) == []
    assert fetcher.requested == []


def test_menu_without_bras_groups_returns_empty_list() -> None:
    """RF-003/RF-006: a readable menu with no devices yields an empty listing."""
    assert BrasUplinkParser(FakeFetcher()).parse(build_menu(), MENU_URL) == []


@pytest.mark.parametrize(
    "title",
    [
        "ANZ-BRAS-00 - (10GB GE1/0/1) - Tr&aacute;fico de Red",
        "ANZ-BRAS-00 - (10GB GE1/0/1) - TR&Aacute;FICO DE RED",
        "ANZ-BRAS-00 - (10GB GE1/0/1) - Trafico de Red",
        "ANZ-BRAS-00 - (10GB GE1/0/1) - TRAFICO DE RED",
        "anz-bras-00 - (10gb ge1/0/1) - trafico de red",
        "  ANZ-BRAS-00   -   (10GB  GE1/0/1)   -   Tráfico  de  Red  ",
        "ANZ-BRAS-00 - (10GB GE1/0/1)-Trafico de Red",
    ],
)
def test_name_ignores_suffix_in_any_format_and_is_uppercase(title: str) -> None:
    """RF-003: the suffix is removed regardless of case, accent or spacing; name is uppercase."""
    [interface] = parse_one_page([build_block(title)])

    assert interface.name == "ANZ-BRAS-00 - (10GB GE1/0/1)".replace("  ", " ")


def test_title_without_suffix_is_kept_as_an_interface() -> None:
    """RF-003: a non-summary title without the suffix is not silently lost."""
    [interface] = parse_one_page([build_block("ANZ-BRAS-00 - (10GB GE1/0/1)")])

    assert interface.name == "ANZ-BRAS-00 - (10GB GE1/0/1)"


def test_empty_name_is_kept_as_incomplete_interface() -> None:
    """RF-003/RF-004: a title that is only the suffix leaves `name` as None."""
    [interface] = parse_one_page([build_block("- Trafico de Red")])

    assert interface.name is None
    assert interface.scan_url is not None


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("ANZ-BRAS-00 - (10GB GE1/0/1)", 10.0),
        ("ANZ-BRAS-00 - (100GB GE1/0/1)", 100.0),
        ("ANZ-BRAS-00 - (10gb GE1/0/1)", 10.0),
        ("ANZ-BRAS-00 - (Eth-Trunk11)", None),
        ("ANZ-BRAS-00 - (GB GE1/0/1)", None),
        ("ANZ-BRAS-00 - (10 GB GE1/0/1)", None),
        ("ANZ-BRAS-00 - (10GE1/0/1)", None),
        ("ANZ-BRAS-00", None),
    ],
)
def test_capacity_is_read_from_the_port_name(title: str, expected: float | None) -> None:
    """RF-003: the number before `GB` is the capacity; otherwise it is not obtainable."""
    [interface] = parse_one_page([build_block(f"{title}{SUFFIX}")])

    assert interface.capacity_gbps == expected


@pytest.mark.parametrize(
    "title",
    [
        "Sumatoria ANZ-BRAS-00 - Total de uplink por Agregador",
        "SUMATORIA ANZ-BRAS-00 - Total de uplink",
        "  sumatoria  ANZ-BRAS-00",
        "ANZ-BRAS-00 - Sumatoria (10GB GE1/0/1) - Trafico de Red",
    ],
)
def test_summaries_are_skipped_without_consuming_a_position(title: str) -> None:
    """RF-003: any title containing "Sumatoria" is omitted; positions stay consecutive."""
    blocks = [
        build_block(title),
        build_block(f"A (10GB GE1){SUFFIX}"),
        build_block(title),
        build_block(f"B (10GB GE2){SUFFIX}"),
    ]

    interfaces = parse_one_page(blocks)

    assert [(i.position, i.name) for i in interfaces] == [(1, "A (10GB GE1)"), (2, "B (10GB GE2)")]


@pytest.mark.parametrize(
    ("href", "expected"),
    [
        ("/mrtg/r1.html", "https://scan.example/mrtg/r1.log"),
        ("mrtg/r1.html", "https://scan.example/cgi-bin/bras/mrtg/r1.log"),
        ("https://other.example/mrtg/r1.html", "https://other.example/mrtg/r1.log"),
        ("  /mrtg/r1.html  ", "https://scan.example/mrtg/r1.log"),
        ("/mrtg/r1.html?x=1", "https://scan.example/mrtg/r1.log?x=1"),
        ("/mrtg/r1.v2.html", "https://scan.example/mrtg/r1.v2.log"),
        ("/mrtg/a.html/b.html", "https://scan.example/mrtg/a.html/b.log"),
    ],
)
def test_scan_url_is_absolute_and_ends_in_log(href: str, expected: str) -> None:
    """RF-003: the href is resolved against the device page and `.html` becomes `.log`."""
    [interface] = parse_one_page([build_block(f"A (10GB GE1){SUFFIX}", href)])

    assert interface.scan_url == expected


@pytest.mark.parametrize("href", ["/mrtg/r1.log", "/mrtg/r1", "/mrtg/r1.htm", "/mrtg/", "#", ""])
def test_href_without_html_extension_leaves_scan_url_empty(href: str) -> None:
    """RF-003/RF-004: an href not ending in `.html` makes the interface incomplete."""
    [interface] = parse_one_page([build_block(f"A (10GB GE1){SUFFIX}", href)])

    assert interface.scan_url is None
    assert interface.name == "A (10GB GE1)"


def test_block_without_link_is_kept_as_incomplete_interface() -> None:
    """RF-003/RF-004: a block with title but no anchor is not discarded."""
    [interface] = parse_one_page([build_block(f"A (10GB GE1){SUFFIX}", href=None)])

    assert interface.scan_url is None
    assert interface.name == "A (10GB GE1)"


def test_block_without_graphs_item_is_kept_as_incomplete_interface() -> None:
    """RF-003/RF-004: a block without `li#graficas` is not discarded."""
    block = f'<div class="col-sm-12"><ul><li id="subtitulo"> A (10GB GE1){SUFFIX}</li></ul></div>'

    [interface] = parse_one_page([block])

    assert interface.scan_url is None


def test_block_without_title_is_ignored() -> None:
    """RF-003: a block with no `li#subtitulo` is not an interface."""
    interfaces = parse_one_page([build_block(None), build_block(f"A (10GB GE1){SUFFIX}")])

    assert [(i.position, i.name) for i in interfaces] == [(1, "A (10GB GE1)")]


def test_device_page_with_only_summaries_returns_empty_list() -> None:
    """RF-003/RF-006: structure present but no interface rows yields an empty listing."""
    assert parse_one_page([build_block("Sumatoria ANZ-BRAS-00 - Total de uplink")]) == []


def test_device_page_with_zero_rows_returns_empty_list() -> None:
    """RF-003/RF-006: structure present with zero rows yields an empty listing."""
    assert parse_one_page([]) == []


def test_dirty_html_is_tolerated() -> None:
    """RF-003: stray `<td>`, unclosed tags and repeated ids do not break the parsing."""
    block = (
        '<div class="col-sm-12"><ul><li id="subtitulo"> A (10GB GE1) - Trafico de Red\n'
        '<li id="graficas"><center><a href="/mrtg/r1.html"><img id="graficas"></a>'
        "<br>Max<em>In</em><td>1 Gb/s</td>&nbsp;<td>2 Gb/s</td></center></ul></div>"
    )

    [interface] = parse_one_page([block])

    assert interface.name == "A (10GB GE1)"
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
def test_unreadable_menu_raises(menu: str) -> None:
    """RF-003: a menu without `div.sidebar > ul[role=menu]` makes the page unreadable."""
    fetcher = FakeFetcher()

    with pytest.raises(UnreadablePageError):
        BrasUplinkParser(fetcher).parse(menu, MENU_URL)

    assert fetcher.requested == []


@pytest.mark.parametrize(
    ("page", "missing"),
    [
        (build_device_page(with_content=False), "section.content"),
        (build_device_page(with_row=False), "div.row"),
        (build_device_page(with_column=False), "div.col-md-12"),
        ("", "section.content"),
        ("<html><body><p>Error</p></body></html>", "section.content"),
    ],
)
def test_unreadable_device_page_raises(page: str, missing: str) -> None:
    """RF-003: a device page without its expected structure makes the whole page unreadable."""
    fetcher = FakeFetcher({ANZ_00_URL: page})

    with pytest.raises(UnreadablePageError) as error_info:
        BrasUplinkParser(fetcher).parse(menu_with_anz_00(), MENU_URL)

    assert missing in error_info.value.cause


def test_failure_downloading_a_device_page_reaches_the_caller() -> None:
    """RF-003/RF-010: a failing device page fails the whole Bras page; nothing is swallowed."""
    menu = build_menu(
        build_group(
            "ANZ-BRAS",
            uplink=[
                ("ANZ-BRAS-00", "/cgi-bin/bras/uplink-bras-anz.cgi?UPLINK-ANZ-BRAS-00.dummy"),
                ("ANZ-BRAS-02", "/cgi-bin/bras/uplink-bras-anz.cgi?UPLINK-ANZ-BRAS-02.dummy"),
            ],
        )
    )
    fetcher = FakeFetcher({ANZ_00_URL: build_device_page(build_block(f"A (10GB GE1){SUFFIX}"))})

    with pytest.raises(ScanHttpError):
        BrasUplinkParser(fetcher).parse(menu, MENU_URL)

    assert fetcher.requested == [ANZ_00_URL, ANZ_02_URL]
