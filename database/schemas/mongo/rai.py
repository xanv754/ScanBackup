from database import RaiFieldDatabase


RAI_SCHEMA ={
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            RaiFieldDatabase.NAME,
            RaiFieldDatabase.CAPACITY
        ],
        "properties": {
            RaiFieldDatabase.NAME: {
                "bsonType": "string",
                "description": "Name interface of the Rai layer"
            },
            RaiFieldDatabase.CAPACITY: {
                "bsonType": "double",
                "description": "Capacity of the Rai layer"
            }
        }
    }
}
