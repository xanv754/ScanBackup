from typing import Any, Dict
from scanbackup.domain import IPSourceBBIPField

SOURCE_IP_BBIP_SCHEMA: Dict[str, Dict[str, Any]] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            IPSourceBBIPField.LINK.value,
            IPSourceBBIPField.INTERFACE.value,
            IPSourceBBIPField.STATUS.value,
        ],
        "properties": {
            IPSourceBBIPField.LINK.value: {
                "bsonType": "string",
                "description": "URL link to the device logs",
            },
            IPSourceBBIPField.INTERFACE.value: {
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
