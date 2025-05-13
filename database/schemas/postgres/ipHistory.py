from database import IPHistoryFieldDatabase, TableNameDatabase


IP_HISTORY_SCHEMA = f"""
    CREATE TABLE IF NOT EXISTS {TableNameDatabase.IP_HISTORY} (
        {IPHistoryFieldDatabase.DATE} DATE NOT NULL,
        {IPHistoryFieldDatabase.TIME} TIME NOT NULL,
        {IPHistoryFieldDatabase.BRAS_NAME} VARCHAR(20) NOT NULL,
        {IPHistoryFieldDatabase.IN_PROM} REAL NOT NULL,
        {IPHistoryFieldDatabase.IN_MAX} REAL NOT NULL,
        CONSTRAINT {TableNameDatabase.IP_HISTORY}_pkey PRIMARY KEY (
            {IPHistoryFieldDatabase.DATE}, 
            {IPHistoryFieldDatabase.TIME}, 
            {IPHistoryFieldDatabase.BRAS_NAME}
        )
    )
"""