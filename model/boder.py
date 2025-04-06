from pydantic import BaseModel


class BorderModel(BaseModel):
    """Border data model."""

    interface: str
    model: str
    capacity: int
