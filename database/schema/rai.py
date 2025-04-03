from database.constant.tables import TableNameDatabase
from database.constant.fields import RaiFieldDatabase


RAI_TABLE_SCHEMA = f"""
    CREATE TABLE {TableNameDatabase.CACHING.value} (
        {RaiFieldDatabase.INTERFACE.value} varchar(200) NOT NULL,
        {RaiFieldDatabase.CAPACITY.value} decimal(6, 2) NOT NULL,
        {RaiFieldDatabase.CREATE_AT.value} timestamp DEFAULT NOW(),
        CONSTRAINT PRIMARY KEY {TableNameDatabase.RAI.value} (
            {RaiFieldDatabase.INTERFACE.value},
            {RaiFieldDatabase.CAPACITY.value}
        )
    );
"""
