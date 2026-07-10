from pydantic import BaseModel


class MongoIPSourceBBIPDTO(BaseModel):
    id: str | None = None
    link: str
    device: str
    status: str
    layer: str

    model_config = {"arbitrary_types_allowed": True}

    @classmethod
    def from_mongo(cls, doc: dict) -> "MongoIPSourceBBIPDTO":
        return cls(
            id=str(doc["_id"]),
            **{k: v for k, v in doc.items() if k != "_id"},
        )
