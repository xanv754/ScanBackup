from typing import Any, Dict
from scanbackup.constants import DailySummaryFieldName


DAILY_SUMMARY_SCHEMA: Dict[str, Dict[str, Any]] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            DailySummaryFieldName.NAME,
            DailySummaryFieldName.TYPE,
            DailySummaryFieldName.CAPACITY,
            DailySummaryFieldName.DATE,
            DailySummaryFieldName.TYPE_LAYER,
            DailySummaryFieldName.IN_PROM,
            DailySummaryFieldName.IN_MAX,
            DailySummaryFieldName.OUT_PROM,
            DailySummaryFieldName.OUT_MAX,
            DailySummaryFieldName.USE,
        ],
        "properties": {
            DailySummaryFieldName.NAME: {
                "bsonType": "string",
                "description": "Name interface of the layer",
            },
            DailySummaryFieldName.TYPE: {
                "bsonType": "string",
                "description": "Type of the interface",
            },
            DailySummaryFieldName.CAPACITY: {
                "bsonType": ["int", "long", "double"],
                "description": "Capacity of the layer",
            },
            DailySummaryFieldName.DATE: {
                "bsonType": "string",
                "description": "Date of the traffic",
            },
            DailySummaryFieldName.TYPE_LAYER: {
                "bsonType": "string",
                "description": "Type of the layer",
            },
            DailySummaryFieldName.IN_PROM: {
                "bsonType": ["int", "long", "double"],
                "description": "In prom of the traffic",
            },
            DailySummaryFieldName.OUT_PROM: {
                "bsonType": ["int", "long", "double"],
                "description": "Out prom of the traffic",
            },
            DailySummaryFieldName.IN_MAX: {
                "bsonType": ["int", "long", "double"],
                "description": "In max of the traffic",
            },
            DailySummaryFieldName.OUT_MAX: {
                "bsonType": ["int", "long", "double"],
                "description": "Out max of the traffic",
            },
            DailySummaryFieldName.USE: {
                "bsonType": ["int", "long", "double"],
                "description": "Use of the interface",
            },
        },
    }
}
