from typing import Any, Dict
from scanbackup.constants import IPBrasFieldName


IP_HISTORY_SCHEMA: Dict[str, Dict[str, Any]] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            IPBrasFieldName.DATE,
            IPBrasFieldName.TIME,
            IPBrasFieldName.BRAS_NAME,
            IPBrasFieldName.CAPACITY,
            IPBrasFieldName.IN_PROM,
            IPBrasFieldName.IN_MAX,
            IPBrasFieldName.TYPE
        ],
        "properties": {
            IPBrasFieldName.DATE: {
                "bsonType": "string",
                "description": "Date of the traffic",
            },
            IPBrasFieldName.TIME: {
                "bsonType": "string",
                "description": "Hour of the traffic",
            },
            IPBrasFieldName.BRAS_NAME: {
                "bsonType": "string",
                "description": "Name of Bras",
            },
            IPBrasFieldName.CAPACITY: {
                "bsonType": ["int", "long", "double"],
                "description": "Capacity of the bras layer",
            },
            IPBrasFieldName.IN_PROM: {
                "bsonType": ["int", "long", "double"],
                "description": "In prom of the traffic",
            },
            IPBrasFieldName.IN_MAX: {
                "bsonType": ["int", "long", "double"],
                "description": "In max of the traffic",
            },
            IPBrasFieldName.TYPE: {
                "bsonType": "string",
                "description": "Service of the Caching layer",
            },
        },
    }
}
