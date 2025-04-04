from storage.constant.fields import BordeFieldDatabase

BORDE_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            BordeFieldDatabase.INTERFACE.value,
            BordeFieldDatabase.MODEL.value,
            BordeFieldDatabase.CAPACITY.value
        ],
        "properties": {
            BordeFieldDatabase.INTERFACE.value: {
                "bsonType": "string",
                "description": "Name interface of the border layer"
            },
            BordeFieldDatabase.MODEL.value: {
                "bsonType": "string",
                "description": "Model of the border layer"
            },
            BordeFieldDatabase.CAPACITY.value: {
                "bsonType": "int",
                "description": "Capacity of the border layer"
            }
        } 
    } 
} 