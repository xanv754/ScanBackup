from unittest.mock import Mock

import pytest

from interface_sync.exceptions import ScanHttpError, UnreadablePageError
from interface_sync.scraping.bras.bras_parser import BrasParser
from interface_sync.scraping.html_fetcher import HtmlFetcher

MENU_URL = "https://scan.example/cgi-bin/bras/captura-ip-bras.cgi?IP-CAPTURADAS-SUMA-BRAS.dummy"
UPLINK_URL = "https://scan.example/cgi-bin/bras/uplink-bras-anz.cgi?UPLINK-ANZ-BRAS-00.dummy"
DOWNLINK_URL = "https://scan.example/cgi-bin/bras/downlink-bras-anz.cgi?DOWNLINK-ANZ-BRAS-00.dummy"


def build_menu(uplink: bool = True, downlink: bool = True) -> str:
    def section(title: str, href: str) -> str:
        return (
            f'<li class="nav-item"><a href="#"><p>{title}</p></a><ul>'
            f'<li class="nav-item"><a href="{href}"><p>ANZ-BRAS-00</p></a></li></ul></li>'
        )

    sections = ""
    if uplink:
        sections += section("UPLINK POR BRAS", UPLINK_URL.removeprefix("https://scan.example"))
    if downlink:
        sections += section("DOWNLINK POR BRAS", DOWNLINK_URL.removeprefix("https://scan.example"))
    return (
        '<div class="sidebar"><ul role="menu"><li class="nav-item menu">'
        f'<a href="#"><p>ANZ-BRAS</p></a><ul>{sections}</ul></li></ul></div>'
    )


def build_device_page(*titles: str) -> str:
    blocks = "".join(
        f'<div class="col-sm-12"><ul><li id="subtitulo"> {title}</li>'
        f'<li id="graficas"><a href="/mrtg/{index}-{title[:1]}.html"></a></li></ul></div>'
        for index, title in enumerate(titles)
    )
    return (
        '<section class="content"><div class="row"><div class="col-md-12">'
        f"{blocks}</div></div></section>"
    )


class FakeFetcher:
    def __init__(self, pages: dict[str, str]) -> None:
        self.pages = pages

    def fetch_html(self, url: str) -> str:
        if url not in self.pages:
            raise ScanHttpError(404)
        return self.pages[url]


@pytest.fixture
def fetcher() -> FakeFetcher:
    return FakeFetcher(
        {
            UPLINK_URL: build_device_page(
                "U1 (10GB GE1) - Trafico de Red", "Sumatoria U", "U2 - Trafico de Red"
            ),
            DOWNLINK_URL: build_device_page(
                "D1 (10GB ET1) - Trafico de Red", "D2 - Trafico de Red"
            ),
        }
    )


def test_uplink_comes_first_with_global_positions_and_own_vendor(fetcher: FakeFetcher) -> None:
    """RF-003: Uplink then Downlink, numbered over the whole listing, each with its vendor."""
    interfaces = BrasParser(fetcher).parse(build_menu(), MENU_URL)

    assert [(i.position, i.name, i.vendor) for i in interfaces] == [
        (1, "U1 (10GB GE1)", "Uplink"),
        (2, "U2", "Uplink"),
        (3, "D1 (10GB ET1)", "Downlink"),
        (4, "D2", "Downlink"),
    ]


def test_only_uplink_in_menu_returns_only_uplink(fetcher: FakeFetcher) -> None:
    """RF-003: a direction absent from the menu contributes nothing."""
    interfaces = BrasParser(fetcher).parse(build_menu(downlink=False), MENU_URL)

    assert {i.vendor for i in interfaces} == {"Uplink"}
    assert [i.position for i in interfaces] == [1, 2]


def test_menu_without_devices_returns_empty_list(fetcher: FakeFetcher) -> None:
    """RF-003/RF-006: no device pages in the menu yields an empty listing."""
    assert BrasParser(fetcher).parse(build_menu(uplink=False, downlink=False), MENU_URL) == []


def test_unreadable_menu_raises(fetcher: FakeFetcher) -> None:
    """RF-003: a menu without sidebar fails the whole page."""
    with pytest.raises(UnreadablePageError):
        BrasParser(fetcher).parse("<html></html>", MENU_URL)


def test_downlink_failure_fails_the_whole_page_even_if_uplink_succeeded() -> None:
    """RF-003/RF-010: no partial result is returned when a direction fails."""
    uplink_only = FakeFetcher({UPLINK_URL: build_device_page("U1 - Trafico de Red")})

    with pytest.raises(ScanHttpError):
        BrasParser(uplink_only).parse(build_menu(), MENU_URL)


def test_uplink_and_downlink_are_independent_of_each_other() -> None:
    """RF-003: an Uplink page structure change does not alter what Downlink returns."""
    broken_uplink_page = "<html><body>changed</body></html>"
    fetcher = FakeFetcher(
        {UPLINK_URL: broken_uplink_page, DOWNLINK_URL: build_device_page("D1 - Trafico de Red")}
    )

    with pytest.raises(UnreadablePageError):
        BrasParser(fetcher).parse(build_menu(), MENU_URL)

    downlink_only = BrasParser(fetcher).parse(build_menu(uplink=False), MENU_URL)

    assert [(i.name, i.vendor) for i in downlink_only] == [("D1", "Downlink")]


def test_fetcher_is_injected_not_created() -> None:
    """RF-003: the parser downloads only through the injected fetcher."""
    fetcher = Mock(spec=HtmlFetcher)
    fetcher.fetch_html.return_value = build_device_page("X - Trafico de Red")

    BrasParser(fetcher).parse(build_menu(), MENU_URL)

    assert [call.args[0] for call in fetcher.fetch_html.call_args_list] == [
        UPLINK_URL,
        DOWNLINK_URL,
    ]
