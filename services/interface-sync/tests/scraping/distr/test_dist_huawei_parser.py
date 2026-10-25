import pytest

from interface_sync.exceptions import UnreadablePageError
from interface_sync.scraping.distr.huawei import DistHuaweiParser

PAGE_URL = "https://scan.example/cgi-bin/graficas-trafico.cgi?/dummy"
SUFFIX = " - Trafico de Red"


def build_block(title: str | None, href: str | None = "/mrtg/x.html") -> str:
    title_html = f'<li id="subtitulo" class="list-group-item"> {title}\n</li>' if title else ""
    link_html = f'<a href="{href}" target="_blank"><img src="x.png"></a>' if href else ""
    return (
        '<div class="col-sm-12"><ul class="list-group">'
        f'{title_html}<li id="graficas"><center>{link_html}'
        "<br>Max<em>In</em><td>27.7 Gb/s (69.3%)</td></center></li></ul></div>"
    )


def build_page(*blocks: str, with_main: bool = True, with_row: bool = True) -> str:
    row_open, row_close = ('<div class="row">', "</div>") if with_row else ("", "")
    main_open, main_close = ('<main id="main">', "</main>") if with_main else ("<main>", "</main>")
    return (
        f"<html><body>{main_open}<section>{row_open}{''.join(blocks)}{row_close}</section>"
        f"{main_close}</body></html>"
    )


@pytest.fixture
def parser() -> DistHuaweiParser:
    return DistHuaweiParser()


def test_valid_interface_is_fully_extracted(parser: DistHuaweiParser) -> None:
    """RF-003: name, scan_url, capacity and vendor come from a regular block."""
    html = build_page(
        build_block(
            f"Router CNT-HWDIST-01 (100GE1/0/0 conexión con PFI-HWBORDE-01 100GE1/0/8){SUFFIX}",
            "/mrtg/r27116-ge100.html",
        )
    )

    [interface] = parser.parse(html, PAGE_URL)

    assert interface.position == 1
    assert interface.name == "CNT-HWDIST-01 (100GE1/0/0 CONEXIÓN CON PFI-HWBORDE-01 100GE1/0/8)"
    assert interface.scan_url == "https://scan.example/mrtg/r27116-ge100.log"
    assert interface.capacity_gbps == 100.0
    assert interface.vendor == "Huawei"


@pytest.mark.parametrize(
    "title",
    [
        "Router X (100GE1) - Tr&aacute;fico de Red",
        "ROUTER X (100GE1) - TR&Aacute;FICO DE RED",
        "router x (100ge1) - trafico de red",
        "Router X (100GE1) - Trafico de Rd",
        "  Router   X   (100GE1)   -   Tráfico  de  Red  ",
        "Router X (100GE1)-Trafico de Red",
        "X (100GE1) - Trafico de Red",
    ],
)
def test_name_ignores_prefix_and_suffix_in_any_format_and_is_uppercase(
    parser: DistHuaweiParser, title: str
) -> None:
    """RF-003: prefix and suffix are removed regardless of case, accent or spacing."""
    [interface] = parser.parse(build_page(build_block(title)), PAGE_URL)

    assert interface.name == "X (100GE1)"


def test_title_without_suffix_is_kept_as_an_interface(parser: DistHuaweiParser) -> None:
    """RF-003: a non-summary title without the suffix is not silently lost."""
    [interface] = parser.parse(build_page(build_block("Router X (100GE1)")), PAGE_URL)

    assert interface.name == "X (100GE1)"


def test_title_without_suffix_keeps_its_whole_text(parser: DistHuaweiParser) -> None:
    """RF-003: titles that end abruptly (`-IP`, `NGN LDN`) are kept complete, not lost."""
    html = build_page(
        build_block("Router X (100GE3/1/0 Conexion con Y (Metro HW) (50|100GE8/0/0) -IP"),
        build_block("Router X (100GE3/1/0.3231 conexión con NGN LDN"),
    )

    interfaces = parser.parse(html, PAGE_URL)

    assert [i.name for i in interfaces] == [
        "X (100GE3/1/0 CONEXION CON Y (METRO HW) (50|100GE8/0/0) -IP",
        "X (100GE3/1/0.3231 CONEXIÓN CON NGN LDN",
    ]


def test_router_inside_the_name_is_kept(parser: DistHuaweiParser) -> None:
    """RF-003: only the leading `Router ` prefix is removed."""
    html = build_page(
        build_block(f"Router X (100GE1 conexión con Router NetEngine 8000 X8 y){SUFFIX}")
    )

    [interface] = parser.parse(html, PAGE_URL)

    assert interface.name == "X (100GE1 CONEXIÓN CON ROUTER NETENGINE 8000 X8 Y)"
    assert interface.capacity_gbps == 100.0


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("Router X (100GE1/0/0 conexión con Y 100GE1/0/8)", 100.0),
        ("Router X (10GE1/1/1.2050 conexión con Y)", 10.0),
        ("Router X (10GB GE1/1/2 Conexion con Y)", 10.0),
        ("Router X (100GB Eth-Trunk2 conexión con Y Eth-Trunk3)", 100.0),
        ("Router X (200GB Eth-Trunk12 conexión con Y)", 200.0),
        ("Router X (GE1/1/4(10G) conexión con Y)", 10.0),
        ("Router X (GE1/1/0.301(10G) conexión con Y)", 10.0),
        ("Router X (100ge1/0/0 CONEXIÓN CON Y)", 100.0),
        ("Router X (100GE1/0/0)", 100.0),
        ("Router X (200Eth-Trunk1 conexión con Y Eth-Trunk 10)", 200.0),
        ("Router X (200GB Eth-Trunk1)", 200.0),
        ("Router X (GE1/1/0 conexión con BTO-GW-01-10GE TE2/3)", None),
        ("Router X (GE1/1/0 conexión con Y 100GB Eth-Trunk1)", None),
        ("Router X (GigabitEthernet0/0/0 conexión con Y)", None),
        ("Router X (Eth-Trunk10 conexión con Y Eth-Trunk10)", None),
        ("Router X (Eth-Trunk1)", None),
        ("Router X (GE0/0/0 conexión con GFB y-aww-00)", None),
        ("Router X (GE1/1/0 conexión con Y 200Eth-Trunk1)", None),
        ("Router X (GE1/1/1 conexión con Y)", None),
        ("Router X (10 GE1/0/0 conexión con Y)", None),
        ("Router X", None),
    ],
)
def test_capacity_is_read_from_the_own_port_only(
    parser: DistHuaweiParser, title: str, expected: float | None
) -> None:
    """RF-003: capacity comes from the port before "conexión con", never from the neighbor."""
    [interface] = parser.parse(build_page(build_block(f"{title}{SUFFIX}")), PAGE_URL)

    assert interface.capacity_gbps == expected


def test_capacity_is_a_float(parser: DistHuaweiParser) -> None:
    """RF-003: capacity is returned as float, as the model requires."""
    [interface] = parser.parse(build_page(build_block(f"Router X (10GE1){SUFFIX}")), PAGE_URL)

    assert isinstance(interface.capacity_gbps, float)


@pytest.mark.parametrize(
    "title",
    [
        "Sumatoria DIST - Total",
        "SUMATORIA CNT-HWDIST-01",
        "  sumatoria  X",
        "Router X (100GE1) Sumatoria - Trafico de Red",
    ],
)
def test_summaries_are_skipped_without_consuming_a_position(
    parser: DistHuaweiParser, title: str
) -> None:
    """RF-003: any title containing "Sumatoria" is omitted; positions stay consecutive."""
    html = build_page(
        build_block(title),
        build_block(f"Router A (100GE1){SUFFIX}"),
        build_block(title),
        build_block(f"Router B (100GE2){SUFFIX}"),
    )

    interfaces = parser.parse(html, PAGE_URL)

    assert [(i.position, i.name) for i in interfaces] == [(1, "A (100GE1)"), (2, "B (100GE2)")]


@pytest.mark.parametrize(
    ("href", "expected"),
    [
        ("/mrtg/r1.html", "https://scan.example/mrtg/r1.log"),
        ("mrtg/r1.html", "https://scan.example/cgi-bin/mrtg/r1.log"),
        ("https://other.example/mrtg/r1.html", "https://other.example/mrtg/r1.log"),
        ("  /mrtg/r1.html  ", "https://scan.example/mrtg/r1.log"),
        ("/mrtg/r1.html?x=1", "https://scan.example/mrtg/r1.log?x=1"),
        ("/mrtg/r1.v2.html", "https://scan.example/mrtg/r1.v2.log"),
        ("/mrtg/r27116-ge110.301.html", "https://scan.example/mrtg/r27116-ge110.301.log"),
        ("/mrtg/a.html/b.html", "https://scan.example/mrtg/a.html/b.log"),
    ],
)
def test_scan_url_is_absolute_and_ends_in_log(
    parser: DistHuaweiParser, href: str, expected: str
) -> None:
    """RF-003: the href is resolved against the page URL and `.html` becomes `.log`."""
    html = build_page(build_block(f"Router A (100GE1){SUFFIX}", href))

    [interface] = parser.parse(html, PAGE_URL)

    assert interface.scan_url == expected


@pytest.mark.parametrize("href", ["/mrtg/r1.log", "/mrtg/r1", "/mrtg/r1.htm", "/mrtg/", "#", ""])
def test_href_without_html_extension_leaves_scan_url_empty(
    parser: DistHuaweiParser, href: str
) -> None:
    """RF-003/RF-004: an href not ending in `.html` makes the interface incomplete."""
    html = build_page(build_block(f"Router A (100GE1){SUFFIX}", href))

    [interface] = parser.parse(html, PAGE_URL)

    assert interface.scan_url is None
    assert interface.name == "A (100GE1)"


def test_block_without_link_is_kept_as_incomplete_interface(parser: DistHuaweiParser) -> None:
    """RF-003/RF-004: a block with title but no anchor is not discarded."""
    html = build_page(build_block(f"Router A (100GE1){SUFFIX}", href=None))

    [interface] = parser.parse(html, PAGE_URL)

    assert interface.scan_url is None
    assert interface.name == "A (100GE1)"


def test_block_without_graphs_item_is_kept_as_incomplete_interface(
    parser: DistHuaweiParser,
) -> None:
    """RF-003/RF-004: a block without `li#graficas` is not discarded."""
    block = (
        f'<div class="col-sm-12"><ul><li id="subtitulo"> Router A (100GE1){SUFFIX}</li></ul></div>'
    )

    [interface] = parser.parse(build_page(block), PAGE_URL)

    assert interface.scan_url is None


def test_empty_name_is_kept_as_incomplete_interface(parser: DistHuaweiParser) -> None:
    """RF-003/RF-004: a title that is only prefix and suffix leaves `name` as None."""
    [interface] = parser.parse(build_page(build_block("Router - Trafico de Red")), PAGE_URL)

    assert interface.name is None
    assert interface.capacity_gbps is None
    assert interface.scan_url is not None


def test_block_without_title_is_ignored(parser: DistHuaweiParser) -> None:
    """RF-003: a block with no `li#subtitulo` is not an interface."""
    html = build_page(build_block(None), build_block(f"Router A (100GE1){SUFFIX}"))

    interfaces = parser.parse(html, PAGE_URL)

    assert [(i.position, i.name) for i in interfaces] == [(1, "A (100GE1)")]


def test_every_interface_carries_the_vendor_of_the_parser(parser: DistHuaweiParser) -> None:
    """RF-003: the vendor is set on every interface, even the incomplete ones."""
    html = build_page(
        build_block(f"Router X (100GE1){SUFFIX}"),
        build_block("Sumatoria Y"),
        build_block(f"Router Z{SUFFIX}", href=None),
        build_block(f"Router W{SUFFIX}", href="/mrtg/w.log"),
    )

    interfaces = parser.parse(html, PAGE_URL)

    assert len(interfaces) == 3
    assert {interface.vendor for interface in interfaces} == {"Huawei"}


def test_positions_follow_page_order(parser: DistHuaweiParser) -> None:
    """RF-003: interfaces keep the page order with consecutive positions."""
    html = build_page(*(build_block(f"Router R{i} (100GE{i}){SUFFIX}") for i in range(1, 6)))

    interfaces = parser.parse(html, PAGE_URL)

    assert [(i.position, i.name) for i in interfaces] == [
        (index, f"R{index} (100GE{index})") for index in range(1, 6)
    ]


def test_structure_without_rows_returns_empty_list(parser: DistHuaweiParser) -> None:
    """RF-003/RF-006: structure present with zero rows yields an empty listing."""
    assert parser.parse(build_page(), PAGE_URL) == []


def test_only_summaries_returns_empty_list(parser: DistHuaweiParser) -> None:
    """RF-003/RF-006: a page with only summaries yields an empty listing."""
    assert parser.parse(build_page(build_block("Sumatoria DIST")), PAGE_URL) == []


def test_missing_main_raises_unreadable_page(parser: DistHuaweiParser) -> None:
    """RF-003: a page without `main#main` is unreadable."""
    with pytest.raises(UnreadablePageError) as error_info:
        parser.parse(build_page(build_block("X"), with_main=False), PAGE_URL)

    assert "main#main" in error_info.value.cause


def test_missing_row_raises_unreadable_page(parser: DistHuaweiParser) -> None:
    """RF-003: a page with `main#main` but no `div.row` is unreadable."""
    with pytest.raises(UnreadablePageError) as error_info:
        parser.parse(build_page(build_block("X"), with_row=False), PAGE_URL)

    assert "div.row" in error_info.value.cause


@pytest.mark.parametrize(
    "html",
    ["", "plain text, not html", "<html><body><h1>Login</h1></body></html>"],
)
def test_unrelated_content_raises_unreadable_page(parser: DistHuaweiParser, html: str) -> None:
    """RF-003: content that is not the listing page makes the page unreadable."""
    with pytest.raises(UnreadablePageError):
        parser.parse(html, PAGE_URL)


def test_other_layer_structure_is_unreadable(parser: DistHuaweiParser) -> None:
    """RF-003: a menu-style page (Bras/Caching) has no `main#main` and is not parsed."""
    html = '<html><body><div class="sidebar"><ul role="menu"></ul></div></body></html>'

    with pytest.raises(UnreadablePageError):
        parser.parse(html, PAGE_URL)


def test_dirty_html_is_tolerated(parser: DistHuaweiParser) -> None:
    """RF-003: stray `<td>`, unclosed tags and repeated ids do not break the parsing."""
    block = (
        '<div class="col-sm-12"><ul><li id="subtitulo"> Router A (100GE1) - Trafico de Red\n'
        '<li id="graficas"><center><a href="/mrtg/r1.html"><img id="graficas"></a>'
        "<br>Max<em>In</em><td>1 Gb/s</td>&nbsp;<td>2 Gb/s</td></center></ul></div>"
    )

    [interface] = parser.parse(build_page(block), PAGE_URL)

    assert interface.name == "A (100GE1)"
    assert interface.scan_url == "https://scan.example/mrtg/r1.log"
