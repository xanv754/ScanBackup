from enum import Enum
from typing import Any, Dict


class IPSourceBBIPField(str, Enum):
    LINK = "link"
    DEVICE = "device"
    STATUS = "status"
    LAYER = "layer"


SOURCE_IP_BBIP_SCHEMA: Dict[str, Dict[str, Any]] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            IPSourceBBIPField.LINK.value,
            IPSourceBBIPField.DEVICE.value,
            IPSourceBBIPField.STATUS.value,
        ],
        "properties": {
            IPSourceBBIPField.LINK.value: {
                "bsonType": "string",
                "description": "URL link to the device logs",
            },
            IPSourceBBIPField.DEVICE.value: {
                "bsonType": "string",
                "description": "Interface name of the device",
            },
            IPSourceBBIPField.STATUS.value: {
                "bsonType": "string",
                "description": "Current status of the device",
            },
            IPSourceBBIPField.LAYER.value: {
                "bsonType": "string",
                "description": "Layer name of the device",
            },
        },
    }
}
