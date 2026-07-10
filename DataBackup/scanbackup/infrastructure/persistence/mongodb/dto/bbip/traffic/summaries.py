from pydantic import BaseModel
from datetime import date


class MongoTrafficDailySummaryBBIPDTO(BaseModel):
    id: str | None = None
    date: date
    in_prom: float
    out_prom: float
    in_max: float
    out_max: float
    use: float
    device: str

    model_config = {"arbitrary_types_allowed": True}

    @classmethod
    def from_mongo(cls, doc: dict) -> "MongoTrafficDailySummaryBBIPDTO":
        return cls(
            id=str(doc["_id"]),
            **{k: v for k, v in doc.items() if k != "_id"},
        )
