from storage.constant.fields import BrasFieldDatabase

BRAS_SCHEMA ={
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            BrasFieldDatabase.NAME,
            BrasFieldDatabase.TYPE,
            BrasFieldDatabase.CAPACITY
        ],
        "properties": {
            BrasFieldDatabase.NAME: {
                "bsonType": "string",
                "description": "Name of bras of the Bras layer"
            },
            BrasFieldDatabase.TYPE: {
                "bsonType": "string",
                "description": "Type of the Bras layer"
            },
            BrasFieldDatabase.CAPACITY: {
                "bsonType": "int",
                "description": "Capacity of the Bras layer"
            }
        }
    }
}
