from unittest.mock import Mock

import pytest

from interface_sync.exceptions import UnsupportedPageError
from interface_sync.models import PageConfig
from interface_sync.scraping import PageParserFactory
from interface_sync.scraping.borde.huawei import BordeHuaweiParser
from interface_sync.scraping.borde.juniper import BordeJuniperParser
from interface_sync.scraping.bras.bras_parser import BrasParser
from interface_sync.scraping.caching.caching_parser import CachingParser
from interface_sync.scraping.dint.huawei import DintHuaweiParser
from interface_sync.scraping.distr.huawei import DistHuaweiParser
from interface_sync.scraping.ixp.ixp_parser import IxpParser
from interface_sync.scraping.rai.huawei import RaiHuaweiParser

URL = "https://scan.example/page.cgi"


def test_borde_huawei_page_gets_its_parser() -> None:
    """RF-003: Borde + Huawei resolves to BordeHuaweiParser."""
    page = PageConfig(layer="borde", vendor="huawei", url=URL)

    assert isinstance(PageParserFactory(Mock()).create(page), BordeHuaweiParser)


def test_borde_juniper_page_gets_its_parser() -> None:
    """RF-003: Borde + Juniper resolves to BordeJuniperParser."""
    page = PageConfig(layer="borde", vendor="juniper", url=URL)

    assert isinstance(PageParserFactory(Mock()).create(page), BordeJuniperParser)


def test_bras_page_gets_its_parser_with_the_fetcher() -> None:
    """RF-003: Bras + UNDEFINED resolves to BrasParser."""
    page = PageConfig(layer="bras", vendor="undefined", url=URL)

    assert isinstance(PageParserFactory(Mock()).create(page), BrasParser)


def test_caching_page_gets_its_parser_with_the_fetcher() -> None:
    """RF-003: Caching + UNDEFINED resolves to CachingParser."""
    page = PageConfig(layer="caching", vendor="undefined", url=URL)

    assert isinstance(PageParserFactory(Mock()).create(page), CachingParser)


def test_dint_huawei_page_gets_its_parser() -> None:
    """RF-003: Dint + Huawei resolves to DintHuaweiParser."""
    page = PageConfig(layer="dint", vendor="huawei", url=URL)

    assert isinstance(PageParserFactory(Mock()).create(page), DintHuaweiParser)


def test_dist_huawei_page_gets_its_parser() -> None:
    """RF-003: Dist + Huawei resolves to DistHuaweiParser."""
    page = PageConfig(layer="dist", vendor="huawei", url=URL)

    assert isinstance(PageParserFactory(Mock()).create(page), DistHuaweiParser)


def test_ixp_page_gets_its_parser() -> None:
    """RF-003: Ixp + UNDEFINED resolves to IxpParser."""
    page = PageConfig(layer="ixp", vendor="undefined", url=URL)

    assert isinstance(PageParserFactory(Mock()).create(page), IxpParser)


def test_rai_huawei_page_gets_its_parser() -> None:
    """RF-003: Rai + Huawei resolves to RaiHuaweiParser."""
    page = PageConfig(layer="rai", vendor="huawei", url=URL)

    assert isinstance(PageParserFactory(Mock()).create(page), RaiHuaweiParser)


@pytest.mark.parametrize(
    ("layer", "vendor"),
    [
        ("borde", "cisco"),
        ("rai", "juniper"),
        ("borde", None),
        ("ixp", "huawei"),
        ("rai", "undefined"),
        ("bras", "huawei"),
        ("caching", "huawei"),
        ("dint", "juniper"),
        ("dint", "undefined"),
        ("dist", "juniper"),
        ("dist", "undefined"),
    ],
)
def test_unsupported_layer_or_vendor_raises(layer: str, vendor: str | None) -> None:
    """RF-003: a layer/vendor without parser fails the page with a clear cause."""
    page = PageConfig(layer=layer, vendor=vendor, url=URL)

    with pytest.raises(UnsupportedPageError) as error_info:
        PageParserFactory(Mock()).create(page)

    assert layer.upper() in error_info.value.cause
