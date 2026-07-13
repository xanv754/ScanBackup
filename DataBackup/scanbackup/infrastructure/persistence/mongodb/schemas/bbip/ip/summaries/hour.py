from typing import Any, Dict
from scanbackup.domain import IPHourSummaryBBIPField


HOUR_SUMMARY_SCHEMA: Dict[str, Dict[str, Any]] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            IPHourSummaryBBIPField.DATE.value,
            IPHourSummaryBBIPField.TIME.value,
            IPHourSummaryBBIPField.IN_PROM.value,
            IPHourSummaryBBIPField.IN_MAX.value,
            IPHourSummaryBBIPField.DEVICE.value,
        ],
        "properties": {
            IPHourSummaryBBIPField.DATE.value: {
                "bsonType": "string",
                "description": "Date of the traffic",
            },
            IPHourSummaryBBIPField.TIME.value: {
                "bsonType": "string",
                "description": "Rounded hour of the traffic",
            },
            IPHourSummaryBBIPField.IN_PROM.value: {
                "bsonType": ["int", "long", "double"],
                "description": "In prom of the traffic",
            },
            IPHourSummaryBBIPField.IN_MAX.value: {
                "bsonType": ["int", "long", "double"],
                "description": "In max of the traffic",
            },
            IPHourSummaryBBIPField.DEVICE.value: {
                "bsonType": ["objectId"],
                "description": "MongoDB ObjectId referencing the source device in the IP source collection",
            },
        },
    }
}
