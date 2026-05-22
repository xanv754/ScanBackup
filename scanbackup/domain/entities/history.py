from datetime import date, time
from pydantic import BaseModel
from bson import ObjectId


class BBIPEntity(BaseModel):
    """Data structure of the Backbone IP."""

    date: date
    time: time
    in_prom: float
    in_max: float
    out_prom: float
    out_max: float
    id_source: ObjectId


class IPEntity(BaseModel):
    """Data structure of the IP."""

    date: date
    time: time
    in_prom: float
    in_max: float
    id_source: ObjectId
