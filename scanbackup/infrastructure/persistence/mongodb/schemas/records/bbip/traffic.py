from bson import ObjectId
from typing import Any, Dict
from enum import Enum
from pydantic import BaseModel


class BBIPField(str, Enum):
    DATE = "date"
    TIME = "time"
    IN_PROM = "inProm"
    IN_MAX = "inMax"
    OUT_PROM = "outProm"
    OUT_MAX = "outMax"
    DEVICE = "id_source"


class BBIPDocument(BaseModel):
    date: str
    time: str
    in_prom: float
    in_max: float
    out_prom: float
    out_max: float
    device: ObjectId


BBIP_TRAFFIC_SCHEMA: Dict[str, Dict[str, Any]] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            BBIPField.DATE.value,
            BBIPField.TIME.value,
            BBIPField.IN_PROM.value,
            BBIPField.IN_MAX.value,
            BBIPField.OUT_PROM.value,
            BBIPField.OUT_MAX.value,
            BBIPField.DEVICE.value,
        ],
        "properties": {
            BBIPField.DATE.value: {
                "bsonType": "string",
                "description": "Date of the traffic",
            },
            BBIPField.TIME.value: {
                "bsonType": "string",
                "description": "Hour of the traffic",
            },
            BBIPField.IN_PROM.value: {
                "bsonType": ["int", "long", "double"],
                "description": "In prom of the traffic",
            },
            BBIPField.OUT_PROM.value: {
                "bsonType": ["int", "long", "double"],
                "description": "Out prom of the traffic",
            },
            BBIPField.IN_MAX.value: {
                "bsonType": ["int", "long", "double"],
                "description": "In max of the traffic",
            },
            BBIPField.OUT_MAX.value: {
                "bsonType": ["int", "long", "double"],
                "description": "Out max of the traffic",
            },
            BBIPField.DEVICE.value: {
                "bsonType": ["objectId"],
                "description": "MongoDB ObjectId referencing the source device in the BBIP source collection",
            },
        },
    }
}
