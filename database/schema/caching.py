from database.constant.tables import TableNameDatabase
from database.constant.fields import CachingFieldDatabase


CACHING_TABLE_SCHEMA = f"""
    CREATE TABLE {TableNameDatabase.CACHING.value} (
        {CachingFieldDatabase.INTERFACE.value} varchar(260) NOT NULL,
        {CachingFieldDatabase.SERVICE.value} varchar(20) NOT NULL,
        {CachingFieldDatabase.CAPACITY.value} decimal(6, 2) NOT NULL,
        {CachingFieldDatabase.CREATE_AT.value} timestamp DEFAULT NOW(),
        CONSTRAINT PRIMARY KEY {TableNameDatabase.CACHING.value} (
            {CachingFieldDatabase.INTERFACE.value},
            {CachingFieldDatabase.SERVICE.value}
        )
    );
"""
