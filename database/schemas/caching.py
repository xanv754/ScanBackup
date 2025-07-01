from constants import BBIPFieldName


CACHING_SCHEMA ={
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            BBIPFieldName.NAME,
            BBIPFieldName.TYPE,
            BBIPFieldName.CAPACITY,
            BBIPFieldName.DATE,
            BBIPFieldName.TIME,
            BBIPFieldName.IN_PROM,
            BBIPFieldName.IN_MAX,
            BBIPFieldName.OUT_PROM,
            BBIPFieldName.OUT_MAX
        ],
        "properties": {
            BBIPFieldName.NAME: {
                "bsonType": "string",
                "description": "Name interface of the Caching layer"
            },
            BBIPFieldName.TYPE: {
                "bsonType": "string",
                "description": "Service of the Caching layer"
            },
            BBIPFieldName.CAPACITY: {
                "bsonType": ["int", "long", "double"],
                "description": "Capacity of the Caching layer"
            },
            BBIPFieldName.DATE: {
                "bsonType": "string",
                "description": "Date of the traffic"
            },
            BBIPFieldName.TIME: {
                "bsonType": "string",
                "description": "Hour of the traffic"
            },
            BBIPFieldName.IN_PROM: {
                "bsonType": ["int", "long", "double"],
                "description": "In prom of the traffic"
            },
            BBIPFieldName.OUT_PROM: {
                "bsonType": ["int", "long", "double"],
                "description": "Out prom of the traffic"
            },
            BBIPFieldName.IN_MAX: {
                "bsonType": ["int", "long", "double"],
                "description": "In max of the traffic"
            },
            BBIPFieldName.OUT_MAX: {
                "bsonType": ["int", "long", "double"],
                "description": "Out max of the traffic"
            }
        }
    }
}
