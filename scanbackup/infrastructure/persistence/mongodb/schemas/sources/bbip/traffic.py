from enum import Enum
from typing import Any, Dict


class BBIPSourceField(str, Enum):
    LINK = "link"
    INTERFACE = "interface"
    CAPACITY = "capacity"
    TYPE = "type"
    STATUS = "status"
    LAYER = "layer"


SOURCE_TRAFFIC_BBIP_SCHEMA: Dict[str, Dict[str, Any]] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            BBIPSourceField.LINK.value,
            BBIPSourceField.INTERFACE.value,
            BBIPSourceField.CAPACITY.value,
            BBIPSourceField.TYPE.value,
            BBIPSourceField.STATUS.value,
        ],
        "properties": {
            BBIPSourceField.LINK.value: {
                "bsonType": "string",
                "description": "URL link to the device logs",
            },
            BBIPSourceField.INTERFACE.value: {
                "bsonType": "string",
                "description": "Interface name of the device",
            },
            BBIPSourceField.CAPACITY.value: {
                "bsonType": ["int", "long", "double"],
                "description": "Capacity of the device",
            },
            BBIPSourceField.TYPE.value: {
                "bsonType": "string",
                "description": "Type of the device",
            },
            BBIPSourceField.STATUS.value: {
                "bsonType": "string",
                "description": "Current status of the device",
            },
            BBIPSourceField.LAYER.value: {
                "bsonType": "string",
                "description": "Layer name of the device",
            },
        },
    }
}
