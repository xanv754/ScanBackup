import pytest

from interface_sync.exceptions import UnsupportedPageError
from interface_sync.models import PageConfig
from interface_sync.scraping import PageParserFactory
from interface_sync.scraping.borde.huawei import BordeHuaweiParser
from interface_sync.scraping.borde.juniper import BordeJuniperParser

URL = "https://scan.example/page.cgi"


def test_borde_huawei_page_gets_its_parser() -> None:
    """RF-003: Borde + Huawei resolves to BordeHuaweiParser."""
    page = PageConfig(layer="borde", vendor="huawei", url=URL)

    assert isinstance(PageParserFactory().create(page), BordeHuaweiParser)


def test_borde_juniper_page_gets_its_parser() -> None:
    """RF-003: Borde + Juniper resolves to BordeJuniperParser."""
    page = PageConfig(layer="borde", vendor="juniper", url=URL)

    assert isinstance(PageParserFactory().create(page), BordeJuniperParser)


@pytest.mark.parametrize(
    ("layer", "vendor"),
    [("borde", "cisco"), ("rai", "huawei"), ("borde", None), ("ixp", "undefined")],
)
def test_unsupported_layer_or_vendor_raises(layer: str, vendor: str | None) -> None:
    """RF-003: a layer/vendor without parser fails the page with a clear cause."""
    page = PageConfig(layer=layer, vendor=vendor, url=URL)

    with pytest.raises(UnsupportedPageError) as error_info:
        PageParserFactory().create(page)

    assert layer.capitalize() in error_info.value.cause
