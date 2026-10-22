import pytest

from interface_sync.exceptions import UnreadablePageError
from interface_sync.scraping.borde.juniper import BordeJuniperParser

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
def parser() -> BordeJuniperParser:
    return BordeJuniperParser()


def test_valid_interface_is_fully_extracted(parser: BordeJuniperParser) -> None:
    """RF-003: name, scan_url and capacity are obtained from a regular block."""
    html = build_page(
        build_block(
            f"Enlace Internacional COLUMBUS XIX - PFI-JBORDE-MX-00 100GB-et-0/0/12{SUFFIX}",
            "/mrtg/epfi-jborde-mx-00-100et0012.html",
        )
    )

    [interface] = parser.parse(html, PAGE_URL)

    assert interface.position == 1
    assert interface.name == "COLUMBUS XIX - PFI-JBORDE-MX-00 100GB-ET-0/0/12"
    assert interface.scan_url == "https://scan.example/mrtg/epfi-jborde-mx-00-100et0012.log"
    assert interface.capacity_gbps == 100.0


@pytest.mark.parametrize(
    "title",
    [
        "Enlace Internacional X 100GB-et-0/0/12 - Tr&aacute;fico de Red",
        "ENLACE INTERNACIONAL X 100GB-et-0/0/12 - TR&Aacute;FICO DE RED",
        "enlace internacional x 100gb-et-0/0/12 - tr&aacute;fico de red",
        "Enlace Internacional X 100GB-et-0/0/12 - Trafico de Red",
        "ENLACE INTERNACIONAL X 100GB-et-0/0/12 - TRAFICO DE RED",
        "Enlaces Internacionales X 100GB-et-0/0/12 - Trafico De Red",
        "  Enlace   Internacional   X 100GB-et-0/0/12   -   Tráfico  de  Red  ",
        "Enlace Internacional X 100GB-et-0/0/12-Trafico de Red",
    ],
)
def test_name_ignores_prefix_and_suffix_in_any_format(
    parser: BordeJuniperParser, title: str
) -> None:
    """RF-003: prefix and suffix are removed regardless of case, accent, plural or spacing."""
    [interface] = parser.parse(build_page(build_block(title)), PAGE_URL)

    assert interface.name == "X 100GB-ET-0/0/12"


def test_name_is_always_uppercase(parser: BordeJuniperParser) -> None:
    """RF-003: names end up completely in uppercase."""
    html = build_page(
        build_block("Enlace Internacional Columbus xix - pfi 100gb-et-0/0/12" + SUFFIX)
    )

    [interface] = parser.parse(html, PAGE_URL)

    assert interface.name == interface.name.upper() == "COLUMBUS XIX - PFI 100GB-ET-0/0/12"


def test_prefix_and_suffix_inside_the_name_are_kept(parser: BordeJuniperParser) -> None:
    """RF-003: only a leading prefix and a trailing suffix are removed."""
    html = build_page(
        build_block("Enlace Internacional A Tráfico de Red B 100GB-et-0/0/12" + SUFFIX)
    )

    [interface] = parser.parse(html, PAGE_URL)

    assert interface.name == "A TRÁFICO DE RED B 100GB-ET-0/0/12"


def test_title_without_prefix_keeps_its_text(parser: BordeJuniperParser) -> None:
    """RF-003: a title lacking the prefix is not discarded."""
    [interface] = parser.parse(
        build_page(build_block("Otro Enlace 10GB-et-0/0/0" + SUFFIX)), PAGE_URL
    )

    assert interface.name == "OTRO ENLACE 10GB-ET-0/0/0"


@pytest.mark.parametrize(
    "title",
    [
        "Sumatoria Enlaces Internacionales BBIP Juniper" + SUFFIX,
        "SUMATORIA TOTAL",
        "  sumatoria enlaces",
    ],
)
def test_summary_blocks_are_skipped(parser: BordeJuniperParser, title: str) -> None:
    """RF-003: "Sumatoria" blocks are never obtained, in any format."""
    html = build_page(
        build_block(title), build_block("Enlace Internacional A 10GB-et-0/0/0" + SUFFIX)
    )

    interfaces = parser.parse(html, PAGE_URL)

    assert [interface.name for interface in interfaces] == ["A 10GB-ET-0/0/0"]


def test_positions_follow_page_order_without_counting_summaries(
    parser: BordeJuniperParser,
) -> None:
    """RF-003/RF-014: position is the 1-based place among the obtained interfaces."""
    html = build_page(
        build_block("Sumatoria X"),
        build_block("Enlace Internacional A 10GB-et-0/0/0" + SUFFIX, "/mrtg/a.html"),
        build_block("Enlace Internacional B 10GB-et-0/0/1" + SUFFIX, "/mrtg/b.html"),
        build_block("Enlace Internacional C 10GB-et-0/0/2" + SUFFIX, "/mrtg/c.html"),
    )

    interfaces = parser.parse(html, PAGE_URL)

    assert [(i.position, i.name) for i in interfaces] == [
        (1, "A 10GB-ET-0/0/0"),
        (2, "B 10GB-ET-0/0/1"),
        (3, "C 10GB-ET-0/0/2"),
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
    parser: BordeJuniperParser, href: str, expected_url: str
) -> None:
    """RF-003: scan_url is an absolute URL whose .html extension becomes .log."""
    [interface] = parser.parse(
        build_page(build_block("Enlace Internacional A 10GB-et-0/0/0", href)), PAGE_URL
    )

    assert interface.scan_url == expected_url


@pytest.mark.parametrize("href", ["/mrtg/x.png", "/mrtg/x", "/mrtg/x.log", "/mrtg/x.htm", "#"])
def test_href_without_html_extension_gives_no_scan_url(
    parser: BordeJuniperParser, href: str
) -> None:
    """RF-003/RF-004: a link that is not .html leaves the interface incomplete."""
    [interface] = parser.parse(
        build_page(build_block("Enlace Internacional A 10GB-et-0/0/0", href)), PAGE_URL
    )

    assert interface.scan_url is None
    assert interface.name == "A 10GB-ET-0/0/0"


def test_block_without_link_is_kept_as_incomplete(parser: BordeJuniperParser) -> None:
    """RF-003/RF-004: a block without anchor is returned with scan_url None, not dropped."""
    html = build_page(build_block("Enlace Internacional A 10GB-et-0/0/0", href=None))

    [interface] = parser.parse(html, PAGE_URL)

    assert interface.scan_url is None
    assert interface.name == "A 10GB-ET-0/0/0"


def test_block_without_graphs_item_is_kept_as_incomplete(parser: BordeJuniperParser) -> None:
    """RF-003/RF-004: a block lacking li#graficas keeps its name and has no scan_url."""
    html = build_page(
        '<div><ul><li id="subtitulo">'
        "Enlace Internacional A 10GB-et-0/0/0 - Trafico de Red</li></ul></div>"
    )

    [interface] = parser.parse(html, PAGE_URL)

    assert interface.scan_url is None
    assert interface.name == "A 10GB-ET-0/0/0"


def test_block_with_empty_name_is_kept_as_incomplete(parser: BordeJuniperParser) -> None:
    """RF-003/RF-004: a title that is only prefix and suffix gives name None."""
    html = build_page(build_block("Enlace Internacional" + SUFFIX, "/mrtg/x.html"))

    [interface] = parser.parse(html, PAGE_URL)

    assert interface.name is None
    assert interface.scan_url == "https://scan.example/mrtg/x.log"
    assert interface.capacity_gbps is None


def test_block_without_title_is_ignored(parser: BordeJuniperParser) -> None:
    """RF-003: a block that has no li#subtitulo is not an interface."""
    html = build_page(build_block(None), build_block("Enlace Internacional A 10GB-et-0/0/0"))

    interfaces = parser.parse(html, PAGE_URL)

    assert [interface.name for interface in interfaces] == ["A 10GB-ET-0/0/0"]


@pytest.mark.parametrize(
    ("name", "expected_capacity"),
    [
        ("A 100GB-et-0/0/12", 100.0),
        ("A 10GB-et-0/0/0", 10.0),
        ("A 400GB-et-1/2/3", 400.0),
        ("A 100gb-et-0/0/12", 100.0),
        ("A 100GE-et-0/0/12", 100.0),
        ("A 40GE2/0/0", 40.0),
        ("A 100ge-et-0/0/12", 100.0),
        ("A POS6/1/0", None),
        ("A GB-et-0/0/12", None),
        ("A GE-et-0/0/12", None),
        ("A et-0/0/12", None),
        ("A SIN PUERTO", None),
    ],
)
def test_capacity_is_the_number_before_gb_or_ge(
    parser: BordeJuniperParser, name: str, expected_capacity: float | None
) -> None:
    """RF-003: capacity is the number before "GB" or "GE"; None when it cannot be obtained."""
    [interface] = parser.parse(build_page(build_block(f"Enlace Internacional {name}")), PAGE_URL)

    assert interface.capacity_gbps == expected_capacity


def test_capacity_is_a_float(parser: BordeJuniperParser) -> None:
    """RF-003: capacity is a number without unit or conversion, stored as float."""
    [interface] = parser.parse(
        build_page(build_block("Enlace Internacional A 100GB-et-0/0/12")), PAGE_URL
    )

    assert isinstance(interface.capacity_gbps, float)


def test_structure_without_rows_returns_empty_list(parser: BordeJuniperParser) -> None:
    """RF-003/RF-006: an existing structure with zero blocks is not an error here."""
    assert parser.parse(build_page(), PAGE_URL) == []


def test_only_summaries_returns_empty_list(parser: BordeJuniperParser) -> None:
    """RF-003/RF-006: a listing made only of summaries has no interfaces."""
    assert parser.parse(build_page(build_block("Sumatoria A")), PAGE_URL) == []


def test_missing_main_raises_unreadable_page(parser: BordeJuniperParser) -> None:
    """RF-003: a page without main#main is unreadable."""
    with pytest.raises(UnreadablePageError) as error_info:
        parser.parse(build_page(build_block("Enlace Internacional A"), with_main=False), PAGE_URL)

    assert "main#main" in error_info.value.cause


def test_missing_row_raises_unreadable_page(parser: BordeJuniperParser) -> None:
    """RF-003: a page without div.row is unreadable."""
    with pytest.raises(UnreadablePageError) as error_info:
        parser.parse(build_page(build_block("Enlace Internacional A"), with_row=False), PAGE_URL)

    assert "div.row" in error_info.value.cause


@pytest.mark.parametrize("html", ["", "not html at all", "<html><body><p>Error</p></body></html>"])
def test_unrelated_content_raises_unreadable_page(parser: BordeJuniperParser, html: str) -> None:
    """RF-003: content lacking the expected structure is unreadable."""
    with pytest.raises(UnreadablePageError):
        parser.parse(html, PAGE_URL)


def test_dirty_html_is_tolerated(parser: BordeJuniperParser) -> None:
    """RF-003: stray <td> in <center> and repeated ids (as SCAN emits) do not break parsing."""
    html = build_page(
        build_block("Enlace Internacional A 100GB-et-0/0/12" + SUFFIX, "/mrtg/a.html"),
        build_block("Enlace Internacional B 100GB-et-0/0/13" + SUFFIX, "/mrtg/b.html"),
    )

    assert len(parser.parse(html, PAGE_URL)) == 2
