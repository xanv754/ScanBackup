from enum import Enum
from database.constant.tables import TableNameDatabase
from database.constant.fields import BordeFieldDatabase


BORDE_TABLE_SCHEMA = f"""
    CREATE TABLE {TableNameDatabase.BORDE.value} (
        {BordeFieldDatabase.INTERFACE.value} varchar NOT NULL,
        {BordeFieldDatabase.MODEL.value} varchar(10) NOT NULL,
        {BordeFieldDatabase.CAPACITY.value} numeric(5) NOT NULL,
        CONSTRAINT PRIMARY KEY {TableNameDatabase.BRAS.value} (
            {BordeFieldDatabase.INTERFACE.value},
            {BordeFieldDatabase.MODEL.value}
        )
    );
"""
