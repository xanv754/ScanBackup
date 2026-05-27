from enum import Enum
from typing import Any, Dict


class IPDailySummaryBBIPField(str, Enum):
    DATE = "date"
    IN_PROM = "inProm"
    IN_MAX = "inMax"
    DEVICE = "id_source"


DAILY_SUMMARY_SCHEMA: Dict[str, Dict[str, Any]] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            IPDailySummaryBBIPField.DATE.value,
            IPDailySummaryBBIPField.IN_PROM.value,
            IPDailySummaryBBIPField.IN_MAX.value,
            IPDailySummaryBBIPField.DEVICE.value,
        ],
        "properties": {
            IPDailySummaryBBIPField.DATE.value: {
                "bsonType": "string",
                "description": "Date of the traffic",
            },
            IPDailySummaryBBIPField.IN_PROM.value: {
                "bsonType": ["int", "long", "double"],
                "description": "In prom of the traffic",
            },
            IPDailySummaryBBIPField.IN_MAX.value: {
                "bsonType": ["int", "long", "double"],
                "description": "In max of the traffic",
            },
            IPDailySummaryBBIPField.DEVICE.value: {
                "bsonType": ["objectId"],
                "description": "MongoDB ObjectId referencing the source device in the IP source collection",
            },
        },
    }
}
