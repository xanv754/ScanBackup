from database.constant.fields import IPHistoryFieldDatabase

IP_HISTORY_SCHEMA ={
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            IPHistoryFieldDatabase.DATE,
            IPHistoryFieldDatabase.TIME,
            IPHistoryFieldDatabase.BRAS_NAME,
            IPHistoryFieldDatabase.IN_PROM,
            IPHistoryFieldDatabase.IN_MAX,
        ],
        "properties": {
            IPHistoryFieldDatabase.DATE: {
                "bsonType": "string",
                "description": "Date of the traffic"
            },
            IPHistoryFieldDatabase.TIME: {
                "bsonType": "string",
                "description": "Hour of the traffic"
            },
            IPHistoryFieldDatabase.BRAS_NAME: {
                "bsonType": "string",
                "description": "Name of Bras"
            },
            IPHistoryFieldDatabase.IN_PROM: {
                "bsonType": ["int", "long"],
                "description": "In prom of the traffic"
            },
            IPHistoryFieldDatabase.IN_MAX: {
                "bsonType": ["int", "long"],
                "description": "In max of the traffic"
            }
        }
    }
}
