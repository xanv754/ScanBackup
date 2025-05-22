from model import LayerModel, LayerFieldModel

class BrasModel(LayerModel):
    """Bras data model."""
    
    type: str
    capacity: int


class BrasFieldModel(LayerFieldModel):
    """Bras field model."""

    type: str = "type"
    capacity: str = "capacity"
