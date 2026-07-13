from typing import Any, Dict
from scanbackup.domain import TrafficHourSummaryBBIPField


HOUR_SUMMARY_SCHEMA: Dict[str, Dict[str, Any]] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            TrafficHourSummaryBBIPField.DATE.value,
            TrafficHourSummaryBBIPField.TIME.value,
            TrafficHourSummaryBBIPField.IN_PROM.value,
            TrafficHourSummaryBBIPField.IN_MAX.value,
            TrafficHourSummaryBBIPField.OUT_PROM.value,
            TrafficHourSummaryBBIPField.OUT_MAX.value,
            TrafficHourSummaryBBIPField.USE.value,
            TrafficHourSummaryBBIPField.DEVICE.value,
        ],
        "properties": {
            TrafficHourSummaryBBIPField.DATE.value: {
                "bsonType": "string",
                "description": "Date of the traffic",
            },
            TrafficHourSummaryBBIPField.TIME.value: {
                "bsonType": "string",
                "description": "Rounded hour of the traffic",
            },
            TrafficHourSummaryBBIPField.IN_PROM.value: {
                "bsonType": ["int", "long", "double"],
                "description": "In prom of the traffic",
            },
            TrafficHourSummaryBBIPField.OUT_PROM.value: {
                "bsonType": ["int", "long", "double"],
                "description": "Out prom of the traffic",
            },
            TrafficHourSummaryBBIPField.IN_MAX.value: {
                "bsonType": ["int", "long", "double"],
                "description": "In max of the traffic",
            },
            TrafficHourSummaryBBIPField.OUT_MAX.value: {
                "bsonType": ["int", "long", "double"],
                "description": "Out max of the traffic",
            },
            TrafficHourSummaryBBIPField.USE.value: {
                "bsonType": ["int", "long", "double"],
                "description": "Use of the interface",
            },
            TrafficHourSummaryBBIPField.DEVICE.value: {
                "bsonType": ["objectId"],
                "description": "MongoDB ObjectId referencing the source device in the BBIP source collection",
            },
        },
    }
}
