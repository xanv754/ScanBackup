from systemgrd.constants import BBIPFieldName


BRAS_SCHEMA ={
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            BBIPFieldName.NAME,
            BBIPFieldName.TYPE,
            BBIPFieldName.CAPACITY,
            BBIPFieldName.DATE,
            BBIPFieldName.TIME,
            BBIPFieldName.IN_VALUE,
            BBIPFieldName.IN_MAX,
            BBIPFieldName.OUT_VALUE,
            BBIPFieldName.OUT_MAX
        ],
        "properties": {
            BBIPFieldName.NAME: {
                "bsonType": "string",
                "description": "Name of bras of the Bras layer"
            },
            BBIPFieldName.TYPE: {
                "bsonType": "string",
                "description": "Type of the Bras layer"
            },
            BBIPFieldName.CAPACITY: {
                "bsonType": ["int", "long", "double"],
                "description": "Capacity of the Bras layer"
            },
            BBIPFieldName.DATE: {
                "bsonType": "string",
                "description": "Date of the traffic"
            },
            BBIPFieldName.TIME: {
                "bsonType": "string",
                "description": "Hour of the traffic"
            },
            BBIPFieldName.IN_VALUE: {
                "bsonType": ["int", "long", "double"],
                "description": "In prom of the traffic"
            },
            BBIPFieldName.OUT_VALUE: {
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
