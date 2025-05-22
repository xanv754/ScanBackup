from model import LayerModel, LayerFieldModel


class CachingModel(LayerModel):
    """Caching data model."""
    
    service: str
    capacity: float


class CachingFieldModel(LayerFieldModel):
    """Caching field model."""
    
    service: str = "service"
    capacity: str = "capacity"