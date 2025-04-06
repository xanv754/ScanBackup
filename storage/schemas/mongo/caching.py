from storage.constant.fields import CachingFieldDatabase

CACHING_SCHEMA ={
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            CachingFieldDatabase.INTERFACE,
            CachingFieldDatabase.SERVICE,
            CachingFieldDatabase.CAPACITY
        ],
        "properties": {
            CachingFieldDatabase.INTERFACE: {
                "bsonType": "string",
                "description": "Name interface of the caching layer"
            },
            CachingFieldDatabase.SERVICE: {
                "bsonType": "string",
                "description": "Service of the caching layer"
            },
            CachingFieldDatabase.CAPACITY: {
                "bsonType": "double",
                "description": "Capacity of the caching layer"
            }
        }
    }
}
