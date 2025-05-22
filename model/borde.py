from model import LayerModel, LayerFieldModel


class BordeModel(LayerModel):
    """Borde data model."""

    model: str
    capacity: int


class BordeFieldModel(LayerFieldModel):
    """Borde field model."""

    model: str = "model"
    capacity: str = "capacity"
