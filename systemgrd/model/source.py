from pydantic import BaseModel

class Source(BaseModel):
    """Model info of a source."""

    link: str
    name: str
    capacity: str
    model: str