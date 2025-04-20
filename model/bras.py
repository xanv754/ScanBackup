from pydantic import BaseModel


class BrasModel(BaseModel):
    """Bras data model."""
    
    id: str | None
    name: str
    type: str
    capacity: int
    createAt: str
