from pydantic import BaseModel

class RaiModel(BaseModel):
    """Rai data model."""
    interface: str
    capacity: int
