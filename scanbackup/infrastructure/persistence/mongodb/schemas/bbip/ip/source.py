from enum import Enum
from typing import Any, Dict


class IPSourceField(str, Enum):
    LINK = "link"
    DEVICE = "device"
    STATUS = "status"
    LAYER = "layer"


SOURCE_IP_BBIP_SCHEMA: Dict[str, Dict[str, Any]] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            IPSourceField.LINK.value,
            IPSourceField.DEVICE.value,
            IPSourceField.STATUS.value,
        ],
        "properties": {
            IPSourceField.LINK.value: {
                "bsonType": "string",
                "description": "URL link to the device logs",
            },
            IPSourceField.DEVICE.value: {
                "bsonType": "string",
                "description": "Interface name of the device",
            },
            IPSourceField.STATUS.value: {
                "bsonType": "string",
                "description": "Current status of the device",
            },
            IPSourceField.LAYER.value: {
                "bsonType": "string",
                "description": "Layer name of the device",
            },
        },
    }
}
