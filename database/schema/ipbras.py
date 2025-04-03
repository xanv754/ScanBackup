from database.constant.tables import TableNameDatabase
from database.constant.fields import IpBrasFieldDatabase

IP_BRAS_TABLE_SCHEMA = f"""
    CREATE TABLE {TableNameDatabase.IP_BRAS.value} (
        {IpBrasFieldDatabase.NAME.value} varchar(11) PRIMARY KEY,
        {IpBrasFieldDatabase.CREATE_AT.value} timestamp DEFAULT NOW(),
    );
"""
