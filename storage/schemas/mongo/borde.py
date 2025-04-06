from storage.constant.fields import BordeFieldDatabase

BORDE_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            BordeFieldDatabase.INTERFACE,
            BordeFieldDatabase.MODEL,
            BordeFieldDatabase.CAPACITY
        ],
        "properties": {
            BordeFieldDatabase.INTERFACE: {
                "bsonType": "string",
                "description": "Name interface of the border layer"
            },
            BordeFieldDatabase.MODEL: {
                "bsonType": "string",
                "description": "Model of the border layer"
            },
            BordeFieldDatabase.CAPACITY: {
                "bsonType": "int",
                "description": "Capacity of the border layer"
            }
        }
    }
}
