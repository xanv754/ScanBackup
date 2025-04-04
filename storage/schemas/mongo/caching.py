from storage.constant.fields import CachingFieldDatabase

CACHING_SCHEMA ={
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            CachingFieldDatabase.INTERFACE.value,
            CachingFieldDatabase.SERVICE.value,
            CachingFieldDatabase.CAPACITY.value
        ],
        "properties": {
            CachingFieldDatabase.INTERFACE.value: {
                "bsonType": "string",
                "description": "Name interface of the caching layer"
            },
            CachingFieldDatabase.SERVICE.value: {
                "bsonType": "string",
                "description": "Service of the caching layer"
            },
            CachingFieldDatabase.CAPACITY.value: {
                "bsonType": "double",
                "description": "Capacity of the caching layer"
            }
        } 
    } 
} 