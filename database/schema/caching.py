from enum import Enum
from database.constant.tables import TableNameDatabase
from database.constant.fields import CachingFieldDatabase


CACHING_TABLE_SCHEMA = f"""
    CREATE TABLE {TableNameDatabase.CACHING.value} (
        {CachingFieldDatabase.INTERFACE.value} varchar NOT NULL,
        {CachingFieldDatabase.SERVICE.value} varchar(20) NOT NULL,
        {CachingFieldDatabase.CAPACITY.value} decimal(5,3) NOT NULL,
    );
"""
