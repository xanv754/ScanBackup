from pydantic import BaseModel


class BrasModel(BaseModel):
    """Bras data model."""
    name: str
    type: str
    capacity: int
