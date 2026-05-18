from enum import Enum
from typing import Any, Dict


class IPDailySummaryField(str, Enum):
    DATE = "date"
    IN_PROM = "inProm"
    IN_MAX = "inMax"
    DEVICE = "id_source"


DAILY_SUMMARY_SCHEMA: Dict[str, Dict[str, Any]] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            IPDailySummaryField.DATE.value,
            IPDailySummaryField.IN_PROM.value,
            IPDailySummaryField.IN_MAX.value,
            IPDailySummaryField.DEVICE.value,
        ],
        "properties": {
            IPDailySummaryField.DATE.value: {
                "bsonType": "string",
                "description": "Date of the traffic",
            },
            IPDailySummaryField.IN_PROM.value: {
                "bsonType": ["int", "long", "double"],
                "description": "In prom of the traffic",
            },
            IPDailySummaryField.IN_MAX.value: {
                "bsonType": ["int", "long", "double"],
                "description": "In max of the traffic",
            },
            IPDailySummaryField.DEVICE.value: {
                "bsonType": ["objectId"],
                "description": "MongoDB ObjectId referencing the source device in the IP source collection",
            },
        },
    }
}
