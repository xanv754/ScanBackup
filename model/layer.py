from pydantic import BaseModel


class LayerModel(BaseModel):
    """Layer data model."""
    
    id: str | None
    name: str
    createAt: str


class LayerFieldModel:
    """Layer field model."""

    id: str = "id"
    name: str = "name"
    createAt: str = "createAt"