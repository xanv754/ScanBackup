from systemgrd.constants import DailyReportFieldName


DAILY_REPORT_SCHEMA ={
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            DailyReportFieldName.NAME,
            DailyReportFieldName.TYPE,
            DailyReportFieldName.CAPACITY,
            DailyReportFieldName.DATE,
            DailyReportFieldName.TYPE_LAYER,
            DailyReportFieldName.IN_PROM,
            DailyReportFieldName.IN_MAX,
            DailyReportFieldName.OUT_PROM,
            DailyReportFieldName.OUT_MAX,
            DailyReportFieldName.USE
        ],
        "properties": {
            DailyReportFieldName.NAME: {
                "bsonType": "string",
                "description": "Name interface of the layer"
            },
            DailyReportFieldName.TYPE: {
                "bsonType": "string",
                "description": "Type of the interface"
            },
            DailyReportFieldName.CAPACITY: {
                "bsonType": ["int", "long", "double"],
                "description": "Capacity of the layer"
            },
            DailyReportFieldName.DATE: {
                "bsonType": "string",
                "description": "Date of the traffic"
            },
            DailyReportFieldName.TYPE_LAYER: {
                "bsonType": "string",
                "description": "Type of the layer"
            },
            DailyReportFieldName.IN_PROM: {
                "bsonType": ["int", "long", "double"],
                "description": "In prom of the traffic"
            },
            DailyReportFieldName.OUT_PROM: {
                "bsonType": ["int", "long", "double"],
                "description": "Out prom of the traffic"
            },
            DailyReportFieldName.IN_MAX: {
                "bsonType": ["int", "long", "double"],
                "description": "In max of the traffic"
            },
            DailyReportFieldName.OUT_MAX: {
                "bsonType": ["int", "long", "double"],
                "description": "Out max of the traffic"
            },
            DailyReportFieldName.USE: {
                "bsonType": ["int", "long", "double"],
                "description": "Use of the interface"
            }
        }
    }
}
