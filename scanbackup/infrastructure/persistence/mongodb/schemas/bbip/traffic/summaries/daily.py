from enum import Enum
from typing import Any, Dict


class BBIPDTrafficDailySummaryField(str, Enum):
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
            BBIPDTrafficDailySummaryField.DATE.value,
            BBIPDTrafficDailySummaryField.IN_PROM.value,
            BBIPDTrafficDailySummaryField.IN_MAX.value,
            BBIPDTrafficDailySummaryField.OUT_PROM.value,
            BBIPDTrafficDailySummaryField.OUT_MAX.value,
            BBIPDTrafficDailySummaryField.USE.value,
            BBIPDTrafficDailySummaryField.DEVICE.value,
        ],
        "properties": {
            BBIPDTrafficDailySummaryField.DATE.value: {
                "bsonType": "string",
                "description": "Date of the traffic",
            },
            BBIPDTrafficDailySummaryField.IN_PROM.value: {
                "bsonType": ["int", "long", "double"],
                "description": "In prom of the traffic",
            },
            BBIPDTrafficDailySummaryField.OUT_PROM.value: {
                "bsonType": ["int", "long", "double"],
                "description": "Out prom of the traffic",
            },
            BBIPDTrafficDailySummaryField.IN_MAX.value: {
                "bsonType": ["int", "long", "double"],
                "description": "In max of the traffic",
            },
            BBIPDTrafficDailySummaryField.OUT_MAX.value: {
                "bsonType": ["int", "long", "double"],
                "description": "Out max of the traffic",
            },
            BBIPDTrafficDailySummaryField.USE.value: {
                "bsonType": ["int", "long", "double"],
                "description": "Use of the interface",
            },
            BBIPDTrafficDailySummaryField.DEVICE.value: {
                "bsonType": ["objectId"],
                "description": "MongoDB ObjectId referencing the source device in the BBIP source collection",
            },
        },
    }
}
