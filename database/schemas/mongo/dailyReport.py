from database import DailyReportFieldDatabase


DAILY_REPORT_SCHEMA ={
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            DailyReportFieldDatabase.DATE,
            DailyReportFieldDatabase.ID_LAYER,
            DailyReportFieldDatabase.TYPE_LAYER,
            DailyReportFieldDatabase.IN_PROM,
            DailyReportFieldDatabase.IN_MAX,
            DailyReportFieldDatabase.OUT_PROM,
            DailyReportFieldDatabase.OUT_MAX
        ],
        "properties": {
            DailyReportFieldDatabase.DATE: {
                "bsonType": "string",
                "description": "Date of the traffic"
            },
            DailyReportFieldDatabase.ID_LAYER: {
                "bsonType": "string",
                "description": "ID of the layer"
            },
            DailyReportFieldDatabase.TYPE_LAYER: {
                "bsonType": "string",
                "description": "Type of the layer"
            },
            DailyReportFieldDatabase.IN_PROM: {
                "bsonType": ["int", "long", "double"],
                "description": "In prom of the traffic"
            },
            DailyReportFieldDatabase.OUT_PROM: {
                "bsonType": ["int", "long", "double"],
                "description": "Out prom of the traffic"
            },
            DailyReportFieldDatabase.IN_MAX: {
                "bsonType": ["int", "long", "double"],
                "description": "In max of the traffic"
            },
            DailyReportFieldDatabase.OUT_MAX: {
                "bsonType": ["int", "long", "double"],
                "description": "Out max of the traffic"
            }
        }
    }
}
