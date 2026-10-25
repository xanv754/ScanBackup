import pytest

from interface_sync.scraping.ixp.vendor_extractor import IxpVendorExtractor


@pytest.fixture
def extractor() -> IxpVendorExtractor:
    return IxpVendorExtractor()


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("X (100GB 100GE2/0/8 CONEXIÓN CON SWA IXP BOLEITA POSICION A6)", "A6"),
        ("X (100GB ETH-TRUNK1 CONEXIÓN CON SWB IXP BOLEITA - POSICION B6 - PORTCHANNEL 6)", "B6"),
        ("X (CONEXIÓN CON SWB IXP BOLEITA POSICIÓN C12)", "C12"),
        ("x (conexión con swa ixp boleita posicion a6)", "A6"),
    ],
)
def test_position_code_is_the_vendor(
    extractor: IxpVendorExtractor, name: str, expected: str
) -> None:
    """RF-003: `Posicion <code>` gives the switch position, even if the name ends in other words."""
    assert extractor.extract(name) == expected


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("X (100GB ETH-TRUNK1.1502 CONEXIÓN CON PEERING PRIVADO CANTV - MOVILNET)", "Movilnet"),
        ("X (CONEXIÓN CON PEERING PRIVADO CANTV - VNET)", "Vnet"),
        ("X (CONEXIÓN CON PEERING PRIVADO CANTV - PatriaCell)", "Patriacell"),
        ("X (CONEXIÓN CON PEERING PRIVADO CANTV - THUNDERNET)", "Thundernet"),
        ("X (CONEXIÓN CON PEERING PRIVADO TELEFONICA - CANTV)", "Telefonica"),
        ("X (CONEXIÓN CON PEERING PRIVADO NETUNO - CANTV)", "Netuno"),
        ("X (CONEXIÓN CON PEERING PRIVADO cantv - fibex)", "Fibex"),
        ("X (CONEXIÓN CON PEERING PRIVADO A - B)", "B"),
        ("X (CONEXIÓN CON PEERING PRIVADO CANTV - NAPVE", "Napve"),
    ],
)
def test_peering_vendor_is_the_side_that_is_not_cantv(
    extractor: IxpVendorExtractor, name: str, expected: str
) -> None:
    """RF-003: in a private peering the operator is the side other than CANTV."""
    assert extractor.extract(name) == expected


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("X (CONEXIÓN CON ALGO NUEVO DIGITEL)", "Digitel"),
        ("X (CONEXIÓN CON ALGO NUEVO DIGITEL)  ", "Digitel"),
        ("OPERADOR", "Operador"),
        ("X CONEXIÓN CON Y (FIBEX)", "Fibex"),
    ],
)
def test_last_word_is_the_fallback(extractor: IxpVendorExtractor, name: str, expected: str) -> None:
    """RF-003: without a known pattern, the last word of the name is the vendor."""
    assert extractor.extract(name) == expected


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("X - PEERING PRIVADO CANTV - MDS", "Mds"),
        ("X - POSICION a6", "A6"),
        ("X - PEERING PRIVADO CANTV - iNTER", "Inter"),
    ],
)
def test_vendor_is_capitalized(extractor: IxpVendorExtractor, name: str, expected: str) -> None:
    """RF-003: first letter in uppercase and the rest in lowercase, whatever the input case."""
    assert extractor.extract(name) == expected


def test_position_takes_precedence_over_peering(extractor: IxpVendorExtractor) -> None:
    """RF-003: rule order: the position code wins over a peering pattern in the same name."""
    assert extractor.extract("X POSICION A6 PEERING PRIVADO CANTV - MOVILNET") == "A6"


@pytest.mark.parametrize("name", [None, "", "   "])
def test_empty_name_gives_no_vendor(extractor: IxpVendorExtractor, name: str | None) -> None:
    """RF-003/RF-004: a missing or blank name has no vendor."""
    assert extractor.extract(name) is None


@pytest.mark.parametrize("name", ["()", " ) ", "( )"])
def test_name_without_words_gives_no_vendor(extractor: IxpVendorExtractor, name: str) -> None:
    """RF-003: a name made only of parentheses has nothing to take as vendor."""
    assert extractor.extract(name) is None
