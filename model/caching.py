from pydantic import BaseModel


class CachingModel(BaseModel):
    """Caching data model."""
    interface: str
    service: str
    capacity: int
