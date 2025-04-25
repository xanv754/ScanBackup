from pydantic import BaseModel

class LayerModel(BaseModel):
    """Layer data model."""
    
    id: str | None
    name: str
    createAt: str