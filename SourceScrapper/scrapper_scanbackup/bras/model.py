from pydantic import BaseModel


class BrasPageModel(BaseModel):
    name: str
    url: str
    type_link: str
