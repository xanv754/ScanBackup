from typing import Any, Dict
from scanbackup.domain import TrafficDailySummaryBBIPField


DAILY_SUMMARY_SCHEMA: Dict[str, Dict[str, Any]] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            TrafficDailySummaryBBIPField.DATE.value,
            TrafficDailySummaryBBIPField.IN_PROM.value,
            TrafficDailySummaryBBIPField.IN_MAX.value,
            TrafficDailySummaryBBIPField.OUT_PROM.value,
            TrafficDailySummaryBBIPField.OUT_MAX.value,
            TrafficDailySummaryBBIPField.USE.value,
            TrafficDailySummaryBBIPField.DEVICE.value,
        ],
        "properties": {
            TrafficDailySummaryBBIPField.DATE.value: {
                "bsonType": "string",
                "description": "Date of the traffic",
            },
            TrafficDailySummaryBBIPField.IN_PROM.value: {
                "bsonType": ["int", "long", "double"],
                "description": "In prom of the traffic",
            },
            TrafficDailySummaryBBIPField.OUT_PROM.value: {
                "bsonType": ["int", "long", "double"],
                "description": "Out prom of the traffic",
            },
            TrafficDailySummaryBBIPField.IN_MAX.value: {
                "bsonType": ["int", "long", "double"],
                "description": "In max of the traffic",
            },
            TrafficDailySummaryBBIPField.OUT_MAX.value: {
                "bsonType": ["int", "long", "double"],
                "description": "Out max of the traffic",
            },
            TrafficDailySummaryBBIPField.USE.value: {
                "bsonType": ["int", "long", "double"],
                "description": "Use of the interface",
            },
            TrafficDailySummaryBBIPField.DEVICE.value: {
                "bsonType": ["objectId"],
                "description": "MongoDB ObjectId referencing the source device in the BBIP source collection",
            },
        },
    }
}
