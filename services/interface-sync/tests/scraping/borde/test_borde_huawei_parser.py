import pytest

from interface_sync.exceptions import UnreadablePageError
from interface_sync.scraping.borde.huawei import BordeHuaweiParser

PAGE_URL = "https://scan.example/cgi-bin/borde.cgi?/dummy"
SUFFIX = " - Tr&aacute;fico de Red"


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
def parser() -> BordeHuaweiParser:
    return BordeHuaweiParser()


def test_valid_interface_is_fully_extracted(parser: BordeHuaweiParser) -> None:
    """RF-003: name, scan_url and capacity are obtained from a regular block."""
    html = build_page(
        build_block(
            f"Enlace Internacional LANAUTILUS I - CHC-HWBORDER-00 40GE2/0/0{SUFFIX}",
            "/mrtg/r27696-ge200hwi.html",
        )
    )

    [interface] = parser.parse(html, PAGE_URL)

    assert interface.position == 1
    assert interface.name == "LANAUTILUS I - CHC-HWBORDER-00 40GE2/0/0"
    assert interface.scan_url == "https://scan.example/mrtg/r27696-ge200hwi.log"
    assert interface.capacity_gbps == 40.0
    assert interface.vendor == "HUAWEI"


@pytest.mark.parametrize(
    "title",
    [
        "Enlace Internacional X 40GE1/0/0 - Tr&aacute;fico de Red",
        "ENLACE INTERNACIONAL X 40GE1/0/0 - TR&Aacute;FICO DE RED",
        "enlace internacional x 40ge1/0/0 - tr&aacute;fico de red",
        "Enlace Internacional X 40GE1/0/0 - Trafico de Red",
        "ENLACE INTERNACIONAL X 40GE1/0/0 - TRAFICO DE RED",
        "Enlaces Internacionales X 40GE1/0/0 - Trafico De Red",
        "  Enlace   Internacional   X 40GE1/0/0   -   Tráfico  de  Red  ",
        "Enlace Internacional X 40GE1/0/0-Trafico de Red",
    ],
)
def test_name_ignores_prefix_and_suffix_in_any_format(
    parser: BordeHuaweiParser, title: str
) -> None:
    """RF-003: prefix and suffix are removed regardless of case, accent, plural or spacing."""
    [interface] = parser.parse(build_page(build_block(title)), PAGE_URL)

    assert interface.name == "X 40GE1/0/0"


def test_every_interface_carries_the_vendor_of_the_parser(parser: BordeHuaweiParser) -> None:
    """RF-003: the vendor is set on every interface, even the incomplete ones."""
    html = build_page(
        build_block(f"X 40GE2/0/0{SUFFIX}"),
        build_block("Sumatoria Y"),
        build_block(f"Z{SUFFIX}", href=None),
        build_block(f"W{SUFFIX}", href="/mrtg/w.log"),
    )

    interfaces = parser.parse(html, PAGE_URL)

    assert len(interfaces) == 3
    assert {interface.vendor for interface in interfaces} == {"HUAWEI"}


def test_name_is_always_uppercase(parser: BordeHuaweiParser) -> None:
    """RF-003: names end up completely in uppercase."""
    html = build_page(build_block("Enlace Internacional Lanautilus i - chc 40ge2/0/0" + SUFFIX))

    [interface] = parser.parse(html, PAGE_URL)

    assert interface.name == interface.name.upper() == "LANAUTILUS I - CHC 40GE2/0/0"


def test_prefix_and_suffix_inside_the_name_are_kept(parser: BordeHuaweiParser) -> None:
    """RF-003: only a leading prefix and a trailing suffix are removed."""
    html = build_page(build_block("Enlace Internacional A Tráfico de Red B 40GE1/0/0" + SUFFIX))

    [interface] = parser.parse(html, PAGE_URL)

    assert interface.name == "A TRÁFICO DE RED B 40GE1/0/0"


def test_title_without_prefix_keeps_its_text(parser: BordeHuaweiParser) -> None:
    """RF-003: a title lacking the prefix is not discarded."""
    [interface] = parser.parse(build_page(build_block("Otro Enlace 10GE1/0/0" + SUFFIX)), PAGE_URL)

    assert interface.name == "OTRO ENLACE 10GE1/0/0"


@pytest.mark.parametrize(
    "title",
    [
        "Sumatoria Enlaces Internacionales BBIP Huawei" + SUFFIX,
        "SUMATORIA TOTAL",
        "  sumatoria enlaces",
    ],
)
def test_summary_blocks_are_skipped(parser: BordeHuaweiParser, title: str) -> None:
    """RF-003: "Sumatoria" blocks are never obtained, in any format."""
    html = build_page(build_block(title), build_block("Enlace Internacional A 10GE1/0/0" + SUFFIX))

    interfaces = parser.parse(html, PAGE_URL)

    assert [interface.name for interface in interfaces] == ["A 10GE1/0/0"]


def test_positions_follow_page_order_without_counting_summaries(
    parser: BordeHuaweiParser,
) -> None:
    """RF-003/RF-014: position is the 1-based place among the obtained interfaces."""
    html = build_page(
        build_block("Sumatoria X"),
        build_block("Enlace Internacional A 10GE1/0/0" + SUFFIX, "/mrtg/a.html"),
        build_block("Enlace Internacional B 10GE1/0/1" + SUFFIX, "/mrtg/b.html"),
        build_block("Enlace Internacional C 10GE1/0/2" + SUFFIX, "/mrtg/c.html"),
    )

    interfaces = parser.parse(html, PAGE_URL)

    assert [(i.position, i.name) for i in interfaces] == [
        (1, "A 10GE1/0/0"),
        (2, "B 10GE1/0/1"),
        (3, "C 10GE1/0/2"),
    ]


@pytest.mark.parametrize(
    ("href", "expected_url"),
    [
        ("/mrtg/x.html", "https://scan.example/mrtg/x.log"),
        ("mrtg/x.html", "https://scan.example/cgi-bin/mrtg/x.log"),
        ("https://other.example/mrtg/x.html", "https://other.example/mrtg/x.log"),
        ("  /mrtg/x.html  ", "https://scan.example/mrtg/x.log"),
        ("/mrtg/x.y.html", "https://scan.example/mrtg/x.y.log"),
        ("/mrtg/x.html?a=1", "https://scan.example/mrtg/x.log?a=1"),
    ],
)
def test_scan_url_is_complete_and_uses_log_extension(
    parser: BordeHuaweiParser, href: str, expected_url: str
) -> None:
    """RF-003: scan_url is an absolute URL whose .html extension becomes .log."""
    [interface] = parser.parse(
        build_page(build_block("Enlace Internacional A 10GE1/0/0", href)), PAGE_URL
    )

    assert interface.scan_url == expected_url


@pytest.mark.parametrize("href", ["/mrtg/x.png", "/mrtg/x", "/mrtg/x.log", "/mrtg/x.htm", "#"])
def test_href_without_html_extension_gives_no_scan_url(
    parser: BordeHuaweiParser, href: str
) -> None:
    """RF-003/RF-004: a link that is not .html leaves the interface incomplete."""
    [interface] = parser.parse(
        build_page(build_block("Enlace Internacional A 10GE1/0/0", href)), PAGE_URL
    )

    assert interface.scan_url is None
    assert interface.name == "A 10GE1/0/0"


def test_block_without_link_is_kept_as_incomplete(parser: BordeHuaweiParser) -> None:
    """RF-003/RF-004: a block without anchor is returned with scan_url None, not dropped."""
    html = build_page(build_block("Enlace Internacional A 10GE1/0/0", href=None))

    [interface] = parser.parse(html, PAGE_URL)

    assert interface.scan_url is None
    assert interface.name == "A 10GE1/0/0"


def test_block_without_graphs_item_is_kept_as_incomplete(parser: BordeHuaweiParser) -> None:
    """RF-003/RF-004: a block lacking li#graficas keeps its name and has no scan_url."""
    html = build_page(
        '<div><ul><li id="subtitulo">'
        "Enlace Internacional A 10GE1/0/0 - Trafico de Red</li></ul></div>"
    )

    [interface] = parser.parse(html, PAGE_URL)

    assert interface.scan_url is None
    assert interface.name == "A 10GE1/0/0"


def test_block_with_empty_name_is_kept_as_incomplete(parser: BordeHuaweiParser) -> None:
    """RF-003/RF-004: a title that is only prefix and suffix gives name None."""
    html = build_page(build_block("Enlace Internacional" + SUFFIX, "/mrtg/x.html"))

    [interface] = parser.parse(html, PAGE_URL)

    assert interface.name is None
    assert interface.scan_url == "https://scan.example/mrtg/x.log"
    assert interface.capacity_gbps is None


def test_block_without_title_is_ignored(parser: BordeHuaweiParser) -> None:
    """RF-003: a block that has no li#subtitulo is not an interface."""
    html = build_page(build_block(None), build_block("Enlace Internacional A 10GE1/0/0"))

    interfaces = parser.parse(html, PAGE_URL)

    assert [interface.name for interface in interfaces] == ["A 10GE1/0/0"]


@pytest.mark.parametrize(
    ("name", "expected_capacity"),
    [
        ("A 40GE2/0/0", 40.0),
        ("A 100GE1/0/0", 100.0),
        ("A 10GE0/1/2", 10.0),
        ("A 40ge2/0/0", 40.0),
        ("A POS6/1/0", None),
        ("A 100GB-ET-0/0/12", None),
        ("A GE2/0/0", None),
        ("A SIN PUERTO", None),
    ],
)
def test_capacity_is_the_number_before_ge(
    parser: BordeHuaweiParser, name: str, expected_capacity: float | None
) -> None:
    """RF-003: capacity is the number before "GE"; None when it cannot be obtained."""
    [interface] = parser.parse(build_page(build_block(f"Enlace Internacional {name}")), PAGE_URL)

    assert interface.capacity_gbps == expected_capacity


def test_capacity_is_a_float(parser: BordeHuaweiParser) -> None:
    """RF-003: capacity is a number without unit or conversion, stored as float."""
    [interface] = parser.parse(
        build_page(build_block("Enlace Internacional A 40GE1/0/0")), PAGE_URL
    )

    assert isinstance(interface.capacity_gbps, float)


def test_structure_without_rows_returns_empty_list(parser: BordeHuaweiParser) -> None:
    """RF-003/RF-006: an existing structure with zero blocks is not an error here."""
    assert parser.parse(build_page(), PAGE_URL) == []


def test_only_summaries_returns_empty_list(parser: BordeHuaweiParser) -> None:
    """RF-003/RF-006: a listing made only of summaries has no interfaces."""
    assert parser.parse(build_page(build_block("Sumatoria A")), PAGE_URL) == []


def test_missing_main_raises_unreadable_page(parser: BordeHuaweiParser) -> None:
    """RF-003: a page without main#main is unreadable."""
    with pytest.raises(UnreadablePageError) as error_info:
        parser.parse(build_page(build_block("Enlace Internacional A"), with_main=False), PAGE_URL)

    assert "main#main" in error_info.value.cause


def test_missing_row_raises_unreadable_page(parser: BordeHuaweiParser) -> None:
    """RF-003: a page without div.row is unreadable."""
    with pytest.raises(UnreadablePageError) as error_info:
        parser.parse(build_page(build_block("Enlace Internacional A"), with_row=False), PAGE_URL)

    assert "div.row" in error_info.value.cause


@pytest.mark.parametrize("html", ["", "not html at all", "<html><body><p>Error</p></body></html>"])
def test_unrelated_content_raises_unreadable_page(parser: BordeHuaweiParser, html: str) -> None:
    """RF-003: content lacking the expected structure is unreadable."""
    with pytest.raises(UnreadablePageError):
        parser.parse(html, PAGE_URL)


def test_dirty_html_is_tolerated(parser: BordeHuaweiParser) -> None:
    """RF-003: stray <td> in <center> and repeated ids (as SCAN emits) do not break parsing."""
    html = build_page(
        build_block("Enlace Internacional A 40GE1/0/0" + SUFFIX, "/mrtg/a.html"),
        build_block("Enlace Internacional B 40GE1/0/1" + SUFFIX, "/mrtg/b.html"),
    )

    assert len(parser.parse(html, PAGE_URL)) == 2
