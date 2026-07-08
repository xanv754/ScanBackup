from typing import Any, Dict
from scanbackup.domain import IPActiveBBIPField


IP_HISTORY_SCHEMA: Dict[str, Dict[str, Any]] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            IPActiveBBIPField.DATE.value,
            IPActiveBBIPField.TIME.value,
            IPActiveBBIPField.IN_PROM.value,
            IPActiveBBIPField.IN_MAX.value,
            IPActiveBBIPField.DEVICE.value,
        ],
        "properties": {
            IPActiveBBIPField.DATE.value: {
                "bsonType": "string",
                "description": "Data date",
            },
            IPActiveBBIPField.TIME.value: {
                "bsonType": "string",
                "description": "Data Hour",
            },
            IPActiveBBIPField.IN_PROM.value: {
                "bsonType": ["int", "long", "double"],
                "description": "In prom of IP actives",
            },
            IPActiveBBIPField.IN_MAX.value: {
                "bsonType": ["int", "long", "double"],
                "description": "In max of IP actives",
            },
            IPActiveBBIPField.DEVICE.value: {
                "bsonType": ["objectId"],
                "description": "MongoDB ObjectId referencing the source device in the IP source collection",
            },
        },
    }
}
