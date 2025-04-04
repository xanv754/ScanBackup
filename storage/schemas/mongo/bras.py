from storage.constant.fields import BrasFieldDatabase

BRAS_SCHEMA ={
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            BrasFieldDatabase.NAME.value,
            BrasFieldDatabase.TYPE.value,
            BrasFieldDatabase.CAPACITY.value
        ],
        "properties": {
            BrasFieldDatabase.NAME.value: {
                "bsonType": "string",
                "description": "Name of bras of the bras layer"
            },
            BrasFieldDatabase.TYPE.value: {
                "bsonType": "string",
                "description": "Type of the bras layer"
            },
            BrasFieldDatabase.CAPACITY.value: {
                "bsonType": "int",
                "description": "Capacity of the bras layer"
            }
        } 
    } 
} 