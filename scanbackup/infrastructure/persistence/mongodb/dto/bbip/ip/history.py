from pydantic import BaseModel
from datetime import date, time


class MongoIPHistoryBBIPDTO(BaseModel):
    id: str
    date: date
    time: time
    in_prom: float
    in_max: float
    device: str

    model_config = {"arbitrary_types_allowed": True}

    @classmethod
    def from_mongo(cls, doc: dict) -> "MongoIPHistoryBBIPDTO":
        return cls(
            id=str(doc["_id"]),
            **{k: v for k, v in doc.items() if k != "_id"},
        )
