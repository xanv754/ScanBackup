from enum import Enum
from typing import Any, Dict


class BBIPDailySummaryField(str, Enum):
    DATE = "date"
    IN_PROM = "inProm"
    OUT_PROM = "outProm"
    IN_MAX = "inMax"
    OUT_MAX = "outMax"
    USE = "use"
    DEVICE = "id_source"


DAILY_SUMMARY_SCHEMA: Dict[str, Dict[str, Any]] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            BBIPDailySummaryField.DATE.value,
            BBIPDailySummaryField.IN_PROM.value,
            BBIPDailySummaryField.IN_MAX.value,
            BBIPDailySummaryField.OUT_PROM.value,
            BBIPDailySummaryField.OUT_MAX.value,
            BBIPDailySummaryField.USE.value,
            BBIPDailySummaryField.DEVICE.value,
        ],
        "properties": {
            BBIPDailySummaryField.DATE.value: {
                "bsonType": "string",
                "description": "Date of the traffic",
            },
            BBIPDailySummaryField.IN_PROM.value: {
                "bsonType": ["int", "long", "double"],
                "description": "In prom of the traffic",
            },
            BBIPDailySummaryField.OUT_PROM.value: {
                "bsonType": ["int", "long", "double"],
                "description": "Out prom of the traffic",
            },
            BBIPDailySummaryField.IN_MAX.value: {
                "bsonType": ["int", "long", "double"],
                "description": "In max of the traffic",
            },
            BBIPDailySummaryField.OUT_MAX.value: {
                "bsonType": ["int", "long", "double"],
                "description": "Out max of the traffic",
            },
            BBIPDailySummaryField.USE.value: {
                "bsonType": ["int", "long", "double"],
                "description": "Use of the interface",
            },
            BBIPDailySummaryField.DEVICE.value: {
                "bsonType": ["objectId"],
                "description": "MongoDB ObjectId referencing the source device in the BBIP source collection",
            },
        },
    }
}
