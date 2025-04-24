from database.constant.fields import CachingFieldDatabase

CACHING_SCHEMA ={
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            CachingFieldDatabase.NAME,
            CachingFieldDatabase.SERVICE,
            CachingFieldDatabase.CAPACITY
        ],
        "properties": {
            CachingFieldDatabase.NAME: {
                "bsonType": "string",
                "description": "Name interface of the Caching layer"
            },
            CachingFieldDatabase.SERVICE: {
                "bsonType": "string",
                "description": "Service of the Caching layer"
            },
            CachingFieldDatabase.CAPACITY: {
                "bsonType": "double",
                "description": "Capacity of the Caching layer"
            }
        }
    }
}
