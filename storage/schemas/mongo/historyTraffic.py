from storage.constant.fields import TrafficHistoryFieldDatabase

HISTORY_TRAFFIC_SCHEMA ={
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            TrafficHistoryFieldDatabase.DATE,
            TrafficHistoryFieldDatabase.TIME,
            TrafficHistoryFieldDatabase.ID_LAYER,
        ],
        "properties": {
            TrafficHistoryFieldDatabase.DATE: {
                "bsonType": "string",
                "description": "Date of the traffic"
            },
            TrafficHistoryFieldDatabase.TIME: {
                "bsonType": "string",
                "description": "Time of the traffic"
            },
            TrafficHistoryFieldDatabase.ID_LAYER: {
                "bsonType": "string",
                "description": "ID of the layer"
            },
            TrafficHistoryFieldDatabase.TYPE_LAYER: {
                "bsonType": "string",
                "description": "Type of the layer"
            },
            TrafficHistoryFieldDatabase.IN_PROM: {
                "bsonType": ["int", "long"],
                "description": "In prom of the traffic"
            },
            TrafficHistoryFieldDatabase.OUT_PROM: {
                "bsonType": ["int", "long"],
                "description": "Out prom of the traffic"
            },
            TrafficHistoryFieldDatabase.IN_MAX: {
                "bsonType": ["int", "long"],
                "description": "In max of the traffic"
            },
            TrafficHistoryFieldDatabase.OUT_MAX: {
                "bsonType": ["int", "long"],
                "description": "Out max of the traffic"
            }
        }
    }
}
