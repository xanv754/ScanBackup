from enum import Enum
from typing import Any, Dict


class IPActiveField(str, Enum):
    DATE = "date"
    TIME = "time"
    IN_PROM = "inProm"
    IN_MAX = "inMax"


IP_HISTORY_SCHEMA: Dict[str, Dict[str, Any]] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            IPActiveField.DATE.value,
            IPActiveField.TIME.value,
            IPActiveField.IN_PROM.value,
            IPActiveField.IN_MAX.value,
        ],
        "properties": {
            IPActiveField.DATE.value: {
                "bsonType": "string",
                "description": "Data date",
            },
            IPActiveField.TIME.value: {
                "bsonType": "string",
                "description": "Data Hour",
            },
            IPActiveField.IN_PROM.value: {
                "bsonType": ["int", "long", "double"],
                "description": "In prom of IP actives",
            },
            IPActiveField.IN_MAX.value: {
                "bsonType": ["int", "long", "double"],
                "description": "In max of IP actives",
            },
        },
    }
}
