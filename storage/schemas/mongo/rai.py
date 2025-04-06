from storage.constant.fields import RaiFieldDatabase

RAI_SCHEMA ={
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            RaiFieldDatabase.INTERFACE,
            RaiFieldDatabase.CAPACITY
        ],
        "properties": {
            RaiFieldDatabase.INTERFACE: {
                "bsonType": "string",
                "description": "Name interface of the rai layer"
            },
            RaiFieldDatabase.CAPACITY: {
                "bsonType": "double",
                "description": "Capacity of the rai layer"
            }
        }
    }
}
