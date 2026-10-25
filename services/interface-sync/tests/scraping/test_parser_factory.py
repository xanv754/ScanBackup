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
    """RF-003: Bras + Undefined resolves to BrasParser."""
    page = PageConfig(layer="bras", vendor="undefined", url=URL)

    assert isinstance(PageParserFactory(Mock()).create(page), BrasParser)


def test_caching_page_gets_its_parser_with_the_fetcher() -> None:
    """RF-003: Caching + Undefined resolves to CachingParser."""
    page = PageConfig(layer="caching", vendor="undefined", url=URL)

    assert isinstance(PageParserFactory(Mock()).create(page), CachingParser)


def test_dint_huawei_page_gets_its_parser() -> None:
    """RF-003: Dint + Huawei resolves to DintHuaweiParser."""
    page = PageConfig(layer="dint", vendor="huawei", url=URL)

    assert isinstance(PageParserFactory(Mock()).create(page), DintHuaweiParser)


@pytest.mark.parametrize(
    ("layer", "vendor"),
    [
        ("borde", "cisco"),
        ("rai", "huawei"),
        ("borde", None),
        ("ixp", "undefined"),
        ("bras", "huawei"),
        ("caching", "huawei"),
        ("dint", "juniper"),
        ("dint", "undefined"),
    ],
)
def test_unsupported_layer_or_vendor_raises(layer: str, vendor: str | None) -> None:
    """RF-003: a layer/vendor without parser fails the page with a clear cause."""
    page = PageConfig(layer=layer, vendor=vendor, url=URL)

    with pytest.raises(UnsupportedPageError) as error_info:
        PageParserFactory(Mock()).create(page)

    assert layer.capitalize() in error_info.value.cause
