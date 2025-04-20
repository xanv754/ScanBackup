from storage.constant.fields import TrafficHistoryFieldDatabase

TRAFFIC_HISTORY_SCHEMA ={
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            TrafficHistoryFieldDatabase.DATE,
            TrafficHistoryFieldDatabase.TIME,
            TrafficHistoryFieldDatabase.ID_LAYER,
            TrafficHistoryFieldDatabase.TYPE_LAYER,
            TrafficHistoryFieldDatabase.IN_PROM,
            TrafficHistoryFieldDatabase.IN_MAX,
            TrafficHistoryFieldDatabase.OUT_PROM,
            TrafficHistoryFieldDatabase.OUT_MAX
        ],
        "properties": {
            TrafficHistoryFieldDatabase.DATE: {
                "bsonType": "string",
                "description": "Date of the traffic"
            },
            TrafficHistoryFieldDatabase.TIME: {
                "bsonType": "string",
                "description": "Hour of the traffic"
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
