from pydantic import BaseModel


class CachingModel(BaseModel):
    """Caching data model."""
    
    id: str | None
    name: str
    service: str
    capacity: float
    createAt: str
