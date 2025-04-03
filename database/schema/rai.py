from enum import Enum
from database.constant.tables import TableNameDatabase
from database.constant.fields import RaiFieldDatabase


RAI_TABLE_SCHEMA = f"""
    CREATE TABLE {TableNameDatabase.CACHING.value} (
        {RaiFieldDatabase.INTERFACE.value} varchar NOT NULL,
        {RaiFieldDatabase.CAPACITY.value} decimal(5,3) NOT NULL
    );
"""
