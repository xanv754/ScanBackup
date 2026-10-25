import pytest

from interface_sync.models import LayerResult, PageResult


def test_page_result_succeeds_without_causes():
    """RF-010: a page succeeds only when neither the scraping nor the database failed."""
    result = PageResult(page_label="BORDE HUAWEI", layer="BORDE")

    assert result.scraping_succeeded
    assert result.database_succeeded
    assert result.succeeded


def test_page_result_with_scraping_cause_fails_only_scraping():
    """A scraping cause fails the page but not the database operation."""
    result = PageResult(page_label="BORDE HUAWEI", layer="BORDE", cause="sin conexión a SCAN")

    assert not result.scraping_succeeded
    assert result.database_succeeded
    assert not result.succeeded


def test_page_result_with_database_cause_keeps_scraping_successful():
    """The database result is kept apart: scraping stays successful while the page fails."""
    result = PageResult(
        page_label="BORDE HUAWEI", layer="BORDE", database_cause="error de base de datos"
    )

    assert result.scraping_succeeded
    assert not result.database_succeeded
    assert not result.succeeded


def test_page_result_with_both_causes_fails_both():
    """Both operations can be reported as failed."""
    result = PageResult(page_label="x", layer="BORDE", cause="a", database_cause="b")

    assert not result.scraping_succeeded
    assert not result.database_succeeded


def test_page_result_requires_a_layer():
    """The layer is mandatory: the layer decommission groups pages by it."""
    with pytest.raises(ValueError, match="layer"):
        PageResult(page_label="x")  # type: ignore[call-arg]


def test_page_result_is_immutable():
    """Results are frozen data."""
    result = PageResult(page_label="x", layer="BORDE")

    with pytest.raises(ValueError, match="frozen"):
        result.cause = "late"  # type: ignore[misc]


def test_layer_result_succeeds_when_decommissioned_or_skipped():
    """A skipped layer is not a database failure of its own."""
    assert LayerResult(layer="BORDE", decommissioned_count=3).succeeded
    assert LayerResult(layer="BORDE", skipped_reason="páginas fallidas: X").succeeded


def test_layer_result_fails_with_a_database_cause():
    """RF-010: a database failure while decommissioning fails the layer."""
    assert not LayerResult(layer="BORDE", database_cause="error de base de datos").succeeded
