from pydantic import BaseModel


class CachingPageModel(BaseModel):
    name: str
    url: str
