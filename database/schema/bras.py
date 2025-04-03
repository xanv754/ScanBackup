from enum import Enum
from database.constant.tables import TableNameDatabase
from database.constant.fields import BrasFieldDatabase


BRAS_TABLE_SCHEMA = f"""
    CREATE TABLE {TableNameDatabase.BRAS.value} (
        {BrasFieldDatabase.NAME.value} varchar(120) NOT NULL,
        {BrasFieldDatabase.TYPE.value} varchar(10) NOT NULL,
        {BrasFieldDatabase.CAPACITY.value} numeric(5) NOT NULL,
        CONSTRAINT PRIMARY KEY {TableNameDatabase.BRAS.value} (
            {BrasFieldDatabase.NAME.value},
            {BrasFieldDatabase.TYPE.value}
        )
    );
"""
