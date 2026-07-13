from pydantic import BaseModel, Field, field_validator
from bson import ObjectId
from datetime import date, time


class MongoIPHistoryBBIPDTO(BaseModel):
    id: str | None = None
    date: date
    time: time
    in_prom: float = Field(alias="inProm")
    in_max: float = Field(alias="inMax")
    device: str = Field(alias="id_source")

    model_config = {"arbitrary_types_allowed": True, "populate_by_name": True}

    @field_validator("device", mode="before")
    @classmethod
    def _coerce_device_to_str(cls, value: object) -> object:
        return str(value) if isinstance(value, ObjectId) else value

    @classmethod
    def from_mongo(cls, doc: dict) -> "MongoIPHistoryBBIPDTO":
        return cls(
            id=str(doc["_id"]),
            **{k: v for k, v in doc.items() if k != "_id"},
        )
