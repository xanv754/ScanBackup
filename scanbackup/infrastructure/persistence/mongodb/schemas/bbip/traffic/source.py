from typing import Any, Dict
from enum import Enum


class TrafficSourceBBIPField(str, Enum):
    LINK = "link"
    INTERFACE = "interface"
    CAPACITY = "capacity"
    TYPE = "type"
    STATUS = "status"
    LAYER = "layer"
    COMMENTS = "comments"


SOURCE_TRAFFIC_BBIP_SCHEMA: Dict[str, Dict[str, Any]] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            TrafficSourceBBIPField.LINK.value,
            TrafficSourceBBIPField.INTERFACE.value,
            TrafficSourceBBIPField.CAPACITY.value,
            TrafficSourceBBIPField.TYPE.value,
            TrafficSourceBBIPField.STATUS.value,
        ],
        "properties": {
            TrafficSourceBBIPField.LINK.value: {
                "bsonType": "string",
                "description": "URL link to the device logs",
            },
            TrafficSourceBBIPField.INTERFACE.value: {
                "bsonType": "string",
                "description": "Interface name of the device",
            },
            TrafficSourceBBIPField.CAPACITY.value: {
                "bsonType": ["int", "long", "double"],
                "description": "Capacity of the device",
            },
            TrafficSourceBBIPField.TYPE.value: {
                "bsonType": "string",
                "description": "Type of the device",
            },
            TrafficSourceBBIPField.STATUS.value: {
                "bsonType": "string",
                "description": "Current status of the device",
            },
            TrafficSourceBBIPField.LAYER.value: {
                "bsonType": "string",
                "description": "Layer name of the device",
            },
            TrafficSourceBBIPField.COMMENTS.value: {
                "bsonType": "string",
                "description": "Comments of the device",
            },
        },
    }
}
