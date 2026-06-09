from pydantic import BaseModel


class MongoIPDailySummaryBBIPDTO(BaseModel):
    id: str
    in_prom: float
    in_max: float
    device: str

    model_config = {"arbitrary_types_allowed": True}

    @classmethod
    def from_mongo(cls, doc: dict) -> "MongoIPDailySummaryBBIPDTO":
        return cls(
            id=str(doc["_id"]),
            **{k: v for k, v in doc.items() if k != "_id"},
        )
