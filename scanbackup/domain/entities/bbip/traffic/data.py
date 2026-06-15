from enum import Enum
from pydantic import BaseModel, GetCoreSchemaHandler
from pydantic_core import core_schema
from bson import ObjectId
from datetime import date, time
from typing import Any


class TrafficBBIPField(str, Enum):
    DATE = "date"
    TIME = "time"
    IN_PROM = "inProm"
    IN_MAX = "inMax"
    OUT_PROM = "outProm"
    OUT_MAX = "outMax"
    DEVICE = "id_source"


# TODO: Pasar esto a constants/type
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(
            lambda v: ObjectId(v) if not isinstance(v, ObjectId) else v,
            serialization=core_schema.to_string_ser_schema(),
        )


class TrafficBBIPEntity(BaseModel):
    date: date
    time: time
    in_prom: float
    in_max: float
    out_prom: float
    out_max: float
    device: PyObjectId
