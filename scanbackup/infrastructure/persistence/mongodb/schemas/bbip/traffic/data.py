from typing import Any, Dict
from enum import Enum


class TrafficBBIPField(str, Enum):
    DATE = "date"
    TIME = "time"
    IN_PROM = "inProm"
    IN_MAX = "inMax"
    OUT_PROM = "outProm"
    OUT_MAX = "outMax"
    DEVICE = "id_source"


BBIP_TRAFFIC_SCHEMA: Dict[str, Dict[str, Any]] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            TrafficBBIPField.DATE.value,
            TrafficBBIPField.TIME.value,
            TrafficBBIPField.IN_PROM.value,
            TrafficBBIPField.IN_MAX.value,
            TrafficBBIPField.OUT_PROM.value,
            TrafficBBIPField.OUT_MAX.value,
            TrafficBBIPField.DEVICE.value,
        ],
        "properties": {
            TrafficBBIPField.DATE.value: {
                "bsonType": "string",
                "description": "Date of the traffic",
            },
            TrafficBBIPField.TIME.value: {
                "bsonType": "string",
                "description": "Hour of the traffic",
            },
            TrafficBBIPField.IN_PROM.value: {
                "bsonType": ["int", "long", "double"],
                "description": "In prom of the traffic",
            },
            TrafficBBIPField.OUT_PROM.value: {
                "bsonType": ["int", "long", "double"],
                "description": "Out prom of the traffic",
            },
            TrafficBBIPField.IN_MAX.value: {
                "bsonType": ["int", "long", "double"],
                "description": "In max of the traffic",
            },
            TrafficBBIPField.OUT_MAX.value: {
                "bsonType": ["int", "long", "double"],
                "description": "Out max of the traffic",
            },
            TrafficBBIPField.DEVICE.value: {
                "bsonType": ["objectId"],
                "description": "MongoDB ObjectId referencing the source device in the BBIP source collection",
            },
        },
    }
}
