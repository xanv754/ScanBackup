from model.layer import LayerModel


class CachingModel(LayerModel):
    """Caching data model."""
    
    service: str
    capacity: float
