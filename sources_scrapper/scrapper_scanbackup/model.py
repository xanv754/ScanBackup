from pydantic import BaseModel


class SourceModel(BaseModel):
    link: str
    name: str
    capacity: int | float = 0
    type: str
