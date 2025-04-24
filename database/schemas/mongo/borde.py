from database.constant.fields import BordeFieldDatabase

BORDE_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            BordeFieldDatabase.NAME,
            BordeFieldDatabase.MODEL,
            BordeFieldDatabase.CAPACITY
        ],
        "properties": {
            BordeFieldDatabase.NAME: {
                "bsonType": "string",
                "description": "Name interface of the Borde layer"
            },
            BordeFieldDatabase.MODEL: {
                "bsonType": "string",
                "description": "Model of the Borde layer"
            },
            BordeFieldDatabase.CAPACITY: {
                "bsonType": "int",
                "description": "Capacity of the Borde layer"
            }
        }
    }
}
