from pydantic import BaseModel


class MongoTrafficSourceBBIPDTO(BaseModel):
    id: str | None = None
    link: str
    interface: str
    capacity: float
    type: str
    status: str
    layer: str
    comments: str | None = None

    model_config = {"arbitrary_types_allowed": True}

    @classmethod
    def from_mongo(cls, doc: dict) -> "MongoTrafficSourceBBIPDTO":
        return cls(
            id=str(doc["_id"]),
            **{k: v for k, v in doc.items() if k != "_id"},
        )
