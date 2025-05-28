from database import TableNameDatabase, DailyReportFieldDatabase


DAILY_REPORT_SCHEMA = f"""
    CREATE TABLE IF NOT EXISTS {TableNameDatabase.DAILY_REPORT} (
        {DailyReportFieldDatabase.DATE} DATE NOT NULL,
        {DailyReportFieldDatabase.ID_LAYER} INTEGER NOT NULL,
        {DailyReportFieldDatabase.TYPE_LAYER} VARCHAR(15) NOT NULL,
        {DailyReportFieldDatabase.IN_PROM} REAL NOT NULL,
        {DailyReportFieldDatabase.OUT_PROM} REAL NOT NULL,
        {DailyReportFieldDatabase.IN_MAX} REAL NOT NULL,
        {DailyReportFieldDatabase.OUT_MAX} REAL NOT NULL,
        CONSTRAINT {TableNameDatabase.DAILY_REPORT}_pkey PRIMARY KEY (
            {DailyReportFieldDatabase.DATE}, 
            {DailyReportFieldDatabase.ID_LAYER},
        )
    )
"""