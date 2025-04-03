from database.constant.tables import TableNameDatabase
from database.constant.fields import BordeFieldDatabase


BORDE_TABLE_SCHEMA = f"""
    CREATE TABLE {TableNameDatabase.BORDE.value} (
        {BordeFieldDatabase.INTERFACE.value} varchar(100) NOT NULL,
        {BordeFieldDatabase.MODEL.value} varchar(10) NOT NULL,
        {BordeFieldDatabase.CAPACITY.value} numeric(4) NOT NULL,
        {BordeFieldDatabase.CREATE_AT.value} timestamp DEFAULT NOW(),
        CONSTRAINT PRIMARY KEY {TableNameDatabase.BORDE.value} (
            {BordeFieldDatabase.INTERFACE.value},
            {BordeFieldDatabase.MODEL.value}
        )
    );
"""
