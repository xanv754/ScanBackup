from model import LayerModel, LayerFieldModel

class RaiModel(LayerModel):
    """Rai data model."""

    capacity: float


class RaiFieldModel(LayerFieldModel):
    """Rai field model."""

    capacity: str = "capacity"