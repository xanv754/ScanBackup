from unittest.mock import Mock

import pytest

from interface_sync.exceptions import ScanHttpError, UnreadablePageError
from interface_sync.scraping.caching.caching_parser import CachingParser
from interface_sync.scraping.html_fetcher import HtmlFetcher

MENU_URL = "https://scan.example/cgi-bin/chg/trafico-caching.cgi?SUMAS-CACHING.dummy"
SERVICES = {
    "Google": "Suma GOOGLE",
    "Akamai": "Suma AKAMAI",
    "Facebook": "Suma FACEBOOK (META)",
    "Inter": "ALIANZA INTER",
    "Netflix": "Suma NETFLIX",
    "Abatvgo": "Suma ABATVGO",
}


def url_of(vendor: str) -> str:
    return f"https://scan.example/cgi-bin/chg/{vendor.lower()}.cgi"


def build_menu(missing: tuple[str, ...] = ()) -> str:
    entries = "".join(
        f'<li class="nav-item"><a href="/cgi-bin/chg/{vendor.lower()}.cgi"><p>{label}'
        '<span class="badge">1</span></p></a></li>'
        for vendor, label in SERVICES.items()
        if vendor not in missing
    )
    return (
        '<div class="sidebar"><ul role="menu"><li class="nav-item"><a href="#"><p>Sumatorias</p>'
        f"</a><ul>{entries}</ul></li></ul></div>"
    )


def build_service_page(*titles: str) -> str:
    blocks = "".join(
        f'<div class="col-sm-12"><ul><li id="subtitulo"> {title}</li>'
        f'<li id="graficas"><a href="/mrtg/{index}.html"></a></li></ul></div>'
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
            url_of("Google"): build_service_page("Router G1 (100GE1)", "Sumatoria G"),
            url_of("Akamai"): build_service_page("Router A1 (Eth-Trunk1)"),
            url_of("Facebook"): build_service_page("Sumatoria FACEBOOK CACHING"),
            url_of("Inter"): build_service_page("Router I1 (100GE3)"),
            url_of("Netflix"): build_service_page("Router N1 (100GE4)", "Router N2 (100GE5)"),
            url_of("Abatvgo"): build_service_page("Router B1 (100GE6)"),
        }
    )


def test_services_are_joined_in_order_with_global_positions_and_own_vendor(
    fetcher: FakeFetcher,
) -> None:
    """RF-003: Google, Akamai, Facebook, Inter, Netflix, Abatvgo; numbered over the page."""
    interfaces = CachingParser(fetcher).parse(build_menu(), MENU_URL)

    assert [(i.position, i.name, i.vendor) for i in interfaces] == [
        (1, "G1 (100GE1)", "GOOGLE"),
        (2, "A1 (ETH-TRUNK1)", "AKAMAI"),
        (3, "I1 (100GE3)", "INTER"),
        (4, "N1 (100GE4)", "NETFLIX"),
        (5, "N2 (100GE5)", "NETFLIX"),
        (6, "B1 (100GE6)", "ABATVGO"),
    ]


def test_service_with_only_summaries_contributes_nothing(fetcher: FakeFetcher) -> None:
    """RF-003: Facebook with only summaries yields zero interfaces and is not an error."""
    interfaces = CachingParser(fetcher).parse(build_menu(), MENU_URL)

    assert "FACEBOOK" not in {i.vendor for i in interfaces}


def test_service_missing_from_menu_contributes_nothing(fetcher: FakeFetcher) -> None:
    """RF-003: a service absent from the menu is skipped; the others are still returned."""
    interfaces = CachingParser(fetcher).parse(build_menu(missing=("Netflix",)), MENU_URL)

    assert "NETFLIX" not in {i.vendor for i in interfaces}
    assert [i.position for i in interfaces] == [1, 2, 3, 4]


def test_menu_without_services_returns_empty_list(fetcher: FakeFetcher) -> None:
    """RF-003/RF-006: a readable menu with no services yields an empty listing."""
    menu = build_menu(missing=tuple(SERVICES))

    assert CachingParser(fetcher).parse(menu, MENU_URL) == []


def test_unreadable_menu_raises(fetcher: FakeFetcher) -> None:
    """RF-003: a menu without sidebar fails the whole page."""
    with pytest.raises(UnreadablePageError):
        CachingParser(fetcher).parse("<html></html>", MENU_URL)


def test_one_failing_service_fails_the_whole_page(fetcher: FakeFetcher) -> None:
    """RF-003/RF-010: no partial result is returned when a service page cannot be fetched."""
    del fetcher.pages[url_of("Inter")]

    with pytest.raises(ScanHttpError):
        CachingParser(fetcher).parse(build_menu(), MENU_URL)


def test_services_are_independent_of_each_other(fetcher: FakeFetcher) -> None:
    """RF-003: a structure change in one service page does not alter what the others return."""
    fetcher.pages[url_of("Google")] = "<html><body>changed</body></html>"

    with pytest.raises(UnreadablePageError):
        CachingParser(fetcher).parse(build_menu(), MENU_URL)

    without_google = CachingParser(fetcher).parse(build_menu(missing=("Google",)), MENU_URL)

    assert {i.vendor for i in without_google} == {"AKAMAI", "INTER", "NETFLIX", "ABATVGO"}


def test_fetcher_is_injected_not_created() -> None:
    """RF-003: the parser downloads only through the injected fetcher, one page per service."""
    fetcher = Mock(spec=HtmlFetcher)
    fetcher.fetch_html.return_value = build_service_page("Router X (100GE1)")

    CachingParser(fetcher).parse(build_menu(), MENU_URL)

    assert [call.args[0] for call in fetcher.fetch_html.call_args_list] == [
        url_of(vendor) for vendor in SERVICES
    ]
