from database import TableNameDatabase, TrafficHistoryFieldDatabase


TRAFFIC_HISTORY_SCHEMA = f"""
    CREATE TABLE IF NOT EXISTS {TableNameDatabase.TRAFFIC_HISTORY} (
        {TrafficHistoryFieldDatabase.DATE} DATE NOT NULL,
        {TrafficHistoryFieldDatabase.TIME} TIME NOT NULL,
        {TrafficHistoryFieldDatabase.ID_LAYER} INTEGER NOT NULL,
        {TrafficHistoryFieldDatabase.TYPE_LAYER} VARCHAR(15) NOT NULL,
        {TrafficHistoryFieldDatabase.IN_PROM} REAL NOT NULL,
        {TrafficHistoryFieldDatabase.OUT_PROM} REAL NOT NULL,
        {TrafficHistoryFieldDatabase.IN_MAX} REAL NOT NULL,
        {TrafficHistoryFieldDatabase.OUT_MAX} REAL NOT NULL,
        CONSTRAINT {TableNameDatabase.TRAFFIC_HISTORY}_pkey PRIMARY KEY (
            {TrafficHistoryFieldDatabase.DATE}, 
            {TrafficHistoryFieldDatabase.TIME}, 
            {TrafficHistoryFieldDatabase.ID_LAYER},
            {TrafficHistoryFieldDatabase.TYPE_LAYER}
        )
    )
"""