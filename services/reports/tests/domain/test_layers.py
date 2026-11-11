from reports.domain.layers import FIXED_LAYERS, LayerCatalog, canonical_layer_name


def names(stored_values: list[str]) -> list[str]:
    """Return the canonical names of the catalog in report order."""
    return [layer.name for layer in LayerCatalog(stored_values).ordered()]


def test_rf034_canonical_name_is_trimmed_and_uppercase() -> None:
    """RF-034: the canonical name is `strip().upper()`."""
    assert canonical_layer_name("  Borde ") == "BORDE"


def test_rf039_fixed_layers_keep_their_exact_order() -> None:
    """RF-039: BORDE, BRAS, CACHING, RAI, DINT, DIST, IXP."""
    assert FIXED_LAYERS == ("BORDE", "BRAS", "CACHING", "RAI", "DINT", "DIST", "IXP")
    assert names(list(reversed(FIXED_LAYERS))) == list(FIXED_LAYERS)


def test_rf039_other_layers_follow_alphabetically() -> None:
    """RF-039: layers outside the fixed list come after, in ascending order."""
    assert names(["ZETA", "IXP", "ALFA", "BORDE", "MID"]) == ["BORDE", "IXP", "ALFA", "MID", "ZETA"]


def test_rf039_missing_fixed_layer_is_not_an_existing_layer() -> None:
    """RF-039: a fixed layer without interfaces is not processed."""
    assert names(["DIST", "BRAS"]) == ["BRAS", "DIST"]


def test_rf034_stored_values_with_different_case_share_a_layer() -> None:
    """RF-034: layers are compared ignoring case and the original values are kept."""
    layers = LayerCatalog(["Borde", "BORDE", " borde"]).ordered()
    assert [layer.name for layer in layers] == ["BORDE"]
    assert layers[0].stored_values == (" borde", "BORDE", "Borde")


def test_rf034_no_stored_layers_gives_empty_catalog() -> None:
    """RF-034: without layers the catalog is empty."""
    assert LayerCatalog([]).ordered() == ()
