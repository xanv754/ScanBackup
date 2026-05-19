from enum import Enum
from typing import Any, Dict


class BBIPActiveSourceField(str, Enum):
    LINK = "link"
    DEVICE = "device"
    ESTATUS = "status"
    LAYER = "layer"


SOURCE_IP_BBIP_SCHEMA: Dict[str, Dict[str, Any]] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            BBIPActiveSourceField.LINK.value,
            BBIPActiveSourceField.DEVICE.value,
            BBIPActiveSourceField.STATUS.value,
        ],
        "properties": {
            BBIPActiveSourceField.LINK.value: {
                "bsonType": "string",
                "description": "URL link to the device logs",
            },
            BBIPActiveSourceField.DEVICE.value: {
                "bsonType": "string",
                "description": "Interface name of the device",
            },
            BBIPActiveSourceField.STATUS.value: {
                "bsonType": "string",
                "description": "Current status of the device",
            },
            BBIPActiveSourceField.LAYER.value: {
                "bsonType": "string",
                "description": "Layer name of the device",
            },
        },
    }
}
