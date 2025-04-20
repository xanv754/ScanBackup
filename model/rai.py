from pydantic import BaseModel

class RaiModel(BaseModel):
    """Rai data model."""

    id: str | None
    name: str
    capacity: float
    createAt: str
