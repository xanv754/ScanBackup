from systemgrd.constants import IPBrasHistoryFieldName


IP_HISTORY_SCHEMA ={
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            IPBrasHistoryFieldName.DATE,
            IPBrasHistoryFieldName.TIME,
            IPBrasHistoryFieldName.BRAS_NAME,
            IPBrasHistoryFieldName.IN_PROM,
            IPBrasHistoryFieldName.IN_MAX,
        ],
        "properties": {
            IPBrasHistoryFieldName.DATE: {
                "bsonType": "string",
                "description": "Date of the traffic"
            },
            IPBrasHistoryFieldName.TIME: {
                "bsonType": "string",
                "description": "Hour of the traffic"
            },
            IPBrasHistoryFieldName.BRAS_NAME: {
                "bsonType": "string",
                "description": "Name of Bras"
            },
            IPBrasHistoryFieldName.IN_PROM: {
                "bsonType": ["int", "long"],
                "description": "In prom of the traffic"
            },
            IPBrasHistoryFieldName.IN_MAX: {
                "bsonType": ["int", "long"],
                "description": "In max of the traffic"
            }
        }
    }
}
