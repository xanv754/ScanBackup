from typing import Any, Dict
from enum import Enum


class BBIPTrafficSourceField(str, Enum):
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
            BBIPTrafficSourceField.LINK.value,
            BBIPTrafficSourceField.INTERFACE.value,
            BBIPTrafficSourceField.CAPACITY.value,
            BBIPTrafficSourceField.TYPE.value,
            BBIPTrafficSourceField.STATUS.value,
        ],
        "properties": {
            BBIPTrafficSourceField.LINK.value: {
                "bsonType": "string",
                "description": "URL link to the device logs",
            },
            BBIPTrafficSourceField.INTERFACE.value: {
                "bsonType": "string",
                "description": "Interface name of the device",
            },
            BBIPTrafficSourceField.CAPACITY.value: {
                "bsonType": ["int", "long", "double"],
                "description": "Capacity of the device",
            },
            BBIPTrafficSourceField.TYPE.value: {
                "bsonType": "string",
                "description": "Type of the device",
            },
            BBIPTrafficSourceField.STATUS.value: {
                "bsonType": "string",
                "description": "Current status of the device",
            },
            BBIPTrafficSourceField.LAYER.value: {
                "bsonType": "string",
                "description": "Layer name of the device",
            },
            BBIPTrafficSourceField.COMMENTS.value: {
                "bsonType": "string",
                "description": "Comments of the device",
            },
        },
    }
}
