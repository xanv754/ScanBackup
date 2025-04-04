from storage.constant.fields import RaiFieldDatabase

RAI_SCHEMA ={
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            RaiFieldDatabase.INTERFACE.value,
            RaiFieldDatabase.CAPACITY.value
        ],
        "properties": {
            RaiFieldDatabase.INTERFACE.value: {
                "bsonType": "string",
                "description": "Name interface of the rai layer"
            },
            RaiFieldDatabase.CAPACITY.value: {
                "bsonType": "double",
                "description": "Capacity of the rai layer"
            }
        } 
    } 
} 